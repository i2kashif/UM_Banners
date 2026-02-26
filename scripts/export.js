#!/usr/bin/env node
/**
 * export.js
 * Universal Metals Pakistan Limited — CWIEME Berlin 2026
 * Puppeteer export script for all 8 banner panels.
 *
 * Output: 6,024 × 14,882 px PNG per panel (sRGB, 150 DPI metadata)
 * Viewport: 3,012 × 7,441 CSS px at deviceScaleFactor: 2
 *
 * Usage:
 *   node scripts/export.js                 # Export all 8 panels
 *   node scripts/export.js --panel 5       # Export single panel
 *   node scripts/export.js --panoramic     # Also export panoramic preview
 *
 * Prerequisites:
 *   npm install puppeteer sharp
 *
 * NOTE: 14,882 px output height is within Chrome's 16,384 px texture limit.
 * Single-pass screenshot is safe — no tiling required.
 */

'use strict';

const path   = require('path');
const fs     = require('fs');
const puppeteer = require('puppeteer');
let sharp;
try {
  sharp = require('sharp');
} catch (e) {
  sharp = null;
}

/* ============================================================
   CONFIGURATION
   ============================================================ */

const CONFIG = {
  // CSS viewport dimensions (before deviceScaleFactor)
  VIEWPORT_WIDTH:       3012,
  VIEWPORT_HEIGHT:      7441,

  // Render scale
  DEVICE_SCALE_FACTOR:  2,

  // Output pixel dimensions (= viewport × DSF)
  OUTPUT_WIDTH:         6024,   // 3012 × 2
  OUTPUT_HEIGHT:        14882,  // 7441 × 2

  // DPI metadata to embed in PNG (150 DPI = 150 px/inch = ~59 px/cm)
  OUTPUT_DPI:           150,

  // Chrome screenshot limit check
  CHROME_MAX_DIMENSION: 16384,

  // Timing
  FONT_WAIT_MS:         2000,   // After document.fonts.ready
  IMAGE_WAIT_MS:        1500,   // Additional wait for images to decode
  IDLE_WAIT_MS:         500,    // After networkidle0

  // Paths
  PANELS_DIR:           path.resolve(__dirname, '..', 'panels'),
  OUTPUT_DIR:           path.resolve(__dirname, '..', 'output', 'png'),
  INDEX_FILE:           path.resolve(__dirname, '..', 'index.html'),

  // Total panels
  TOTAL_PANELS:         8,
};

/* ============================================================
   PANEL MANIFEST
   ============================================================ */

const PANELS = [
  { n: 1, file: 'panel-1.html', name: 'Company Hero',             wall: 'left' },
  { n: 2, file: 'panel-2.html', name: 'Vertical Integration',     wall: 'left' },
  { n: 3, file: 'panel-3.html', name: 'Copper Enamelled Wire',    wall: 'centre' },
  { n: 4, file: 'panel-4.html', name: 'Paper Covered Strip',      wall: 'centre' },
  { n: 5, file: 'panel-5.html', name: 'Copper/Aluminium Rod',     wall: 'centre' },
  { n: 6, file: 'panel-6.html', name: 'Insulation Materials',     wall: 'centre' },
  { n: 7, file: 'panel-7.html', name: 'Quality & Certifications', wall: 'right' },
  { n: 8, file: 'panel-8.html', name: 'Contact / CTA',            wall: 'right' },
];

/* ============================================================
   UTILITY: Format bytes for logging
   ============================================================ */

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
}

/* ============================================================
   UTILITY: Parse CLI arguments
   ============================================================ */

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    singlePanel: null,
    includePanoramic: false,
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--panel' && args[i + 1]) {
      opts.singlePanel = parseInt(args[i + 1], 10);
      i++;
    }
    if (args[i] === '--panoramic') {
      opts.includePanoramic = true;
    }
  }

  return opts;
}

/* ============================================================
   CORE: Export a single panel
   ============================================================ */

async function exportPanel(page, panel, outputDir) {
  const filePath = path.join(CONFIG.PANELS_DIR, panel.file);
  const fileUrl  = 'file://' + filePath;
  const outFile  = path.join(outputDir, `panel-${panel.n}.png`);

  console.log(`\n[${ panel.n }/${ CONFIG.TOTAL_PANELS }] ${panel.name} (${panel.wall} wall)`);
  console.log(`    URL: ${fileUrl}`);

  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Verify source file exists
  if (!fs.existsSync(filePath)) {
    console.error(`    ERROR: Source file not found: ${filePath}`);
    return { success: false, error: 'Source file not found' };
  }

  // Set exact viewport before navigating
  await page.setViewport({
    width:             CONFIG.VIEWPORT_WIDTH,
    height:            CONFIG.VIEWPORT_HEIGHT,
    deviceScaleFactor: CONFIG.DEVICE_SCALE_FACTOR,
  });

  // Navigate to panel
  const navStart = Date.now();
  await page.goto(fileUrl, {
    waitUntil: 'networkidle0',
    timeout:   30000,
  });

  // Wait for fonts to load
  await page.evaluateHandle('document.fonts.ready');
  await new Promise(r => setTimeout(r, CONFIG.FONT_WAIT_MS));

  // Wait for all images to decode
  try {
    await page.evaluate(() =>
      Promise.all(
        [...document.images].map(img =>
          img.complete ? Promise.resolve() : img.decode().catch(() => Promise.resolve())
        )
      )
    );
  } catch (e) {
    // Non-fatal — images may not have a decode() method in all contexts
  }

  await new Promise(r => setTimeout(r, CONFIG.IMAGE_WAIT_MS));

  const navMs = Date.now() - navStart;

  // Verify canvas dimensions via JS
  const canvasInfo = await page.evaluate(() => ({
    bodyW: document.body.scrollWidth,
    bodyH: document.body.scrollHeight,
    panelW: document.querySelector('.panel') ? document.querySelector('.panel').offsetWidth : 0,
    panelH: document.querySelector('.panel') ? document.querySelector('.panel').offsetHeight : 0,
  }));

  console.log(`    Canvas: ${canvasInfo.panelW}×${canvasInfo.panelH} CSS px | nav: ${navMs}ms`);

  // Screenshot — single pass (14,882 px < 16,384 px Chrome limit)
  const screenshotStart = Date.now();
  const buffer = await page.screenshot({
    type:           'png',
    clip: {
      x:      0,
      y:      0,
      width:  CONFIG.VIEWPORT_WIDTH,
      height: CONFIG.VIEWPORT_HEIGHT,
    },
    // captureBeyondViewport not needed — panel fits in viewport exactly
    omitBackground: false,
  });

  const shotMs = Date.now() - screenshotStart;

  // Embed DPI metadata using Sharp if available
  if (sharp) {
    await sharp(buffer)
      .withMetadata({ density: CONFIG.OUTPUT_DPI })
      .toFile(outFile);
    console.log(`    Saved with ${CONFIG.OUTPUT_DPI} DPI metadata: ${outFile}`);
  } else {
    fs.writeFileSync(outFile, buffer);
    console.log(`    Saved (no DPI metadata — install sharp for DPI embedding): ${outFile}`);
  }

  const fileSize = fs.statSync(outFile).size;
  const outputDimensions = `${CONFIG.OUTPUT_WIDTH}×${CONFIG.OUTPUT_HEIGHT}`;

  console.log(`    Output: ${outputDimensions} px | Size: ${formatBytes(fileSize)} | screenshot: ${shotMs}ms`);

  return {
    success:    true,
    panel:      panel.n,
    name:       panel.name,
    outputFile: outFile,
    fileSize:   fileSize,
    navMs:      navMs,
    shotMs:     shotMs,
  };
}

/* ============================================================
   CORE: Export panoramic review page
   ============================================================ */

async function exportPanoramic(page, outputDir) {
  const panoramicDir  = path.resolve(__dirname, '..', 'output', 'preview');
  const fileUrl       = 'file://' + CONFIG.INDEX_FILE;
  const outFile       = path.join(panoramicDir, 'panoramic-review.png');

  console.log('\n[P] Panoramic review page');
  console.log(`    URL: ${fileUrl}`);

  if (!fs.existsSync(panoramicDir)) {
    fs.mkdirSync(panoramicDir, { recursive: true });
  }

  if (!fs.existsSync(CONFIG.INDEX_FILE)) {
    console.error('    ERROR: index.html not found');
    return { success: false };
  }

  // Use a wider viewport for the review page
  await page.setViewport({
    width:             1920,
    height:            1080,
    deviceScaleFactor: 1,
  });

  await page.goto(fileUrl, {
    waitUntil: ['networkidle0', 'load'],
    timeout:   60000,
  });

  await page.evaluateHandle('document.fonts.ready');
  await new Promise(r => setTimeout(r, 4000)); // Wait for all iframes to render

  // Full-page screenshot
  const buffer = await page.screenshot({
    type:     'png',
    fullPage: true,
  });

  fs.writeFileSync(outFile, buffer);

  const fileSize = fs.statSync(outFile).size;
  console.log(`    Saved: ${outFile} (${formatBytes(fileSize)})`);

  return { success: true, outputFile: outFile, fileSize };
}

/* ============================================================
   MAIN
   ============================================================ */

async function main() {
  const opts   = parseArgs();
  const startMs = Date.now();

  console.log('='.repeat(60));
  console.log('UMPL CWIEME Berlin 2026 — Puppeteer Export');
  console.log('='.repeat(60));
  console.log(`Viewport:  ${CONFIG.VIEWPORT_WIDTH} × ${CONFIG.VIEWPORT_HEIGHT} CSS px`);
  console.log(`DSF:       ${CONFIG.DEVICE_SCALE_FACTOR}`);
  console.log(`Output:    ${CONFIG.OUTPUT_WIDTH} × ${CONFIG.OUTPUT_HEIGHT} px @ ${CONFIG.OUTPUT_DPI} DPI`);
  console.log(`Output dir: ${CONFIG.OUTPUT_DIR}`);

  // Safety check: output dimensions within Chrome limit
  const maxDim = Math.max(CONFIG.OUTPUT_WIDTH, CONFIG.OUTPUT_HEIGHT);
  if (maxDim > CONFIG.CHROME_MAX_DIMENSION) {
    console.warn(`\nWARNING: Output dimension ${maxDim} px exceeds Chrome limit of ${CONFIG.CHROME_MAX_DIMENSION} px.`);
    console.warn('Screenshots may be truncated. Consider tiled export strategy.');
  } else {
    console.log(`Chrome limit check: ${maxDim} px < ${CONFIG.CHROME_MAX_DIMENSION} px [OK]`);
  }

  // Determine which panels to export
  let panelsToExport = PANELS;
  if (opts.singlePanel !== null) {
    const p = PANELS.find(p => p.n === opts.singlePanel);
    if (!p) {
      console.error(`\nERROR: Panel ${opts.singlePanel} not found. Valid range: 1–8`);
      process.exit(1);
    }
    panelsToExport = [p];
    console.log(`\nSingle panel mode: Panel ${p.n} — ${p.name}`);
  } else {
    console.log(`\nExporting all ${CONFIG.TOTAL_PANELS} panels`);
  }

  // Launch headless Chrome
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--font-render-hinting=none',       // Consistent font rendering
      '--enable-font-antialiasing',
      '--force-color-profile=srgb',       // Consistent sRGB colour output
      '--disable-lcd-text',
      '--hide-scrollbars',
    ],
  });

  const page = await browser.newPage();

  // Disable JS execution in panels (panels are static HTML/CSS)
  // Comment this out if panel scripts need to run
  // await page.setJavaScriptEnabled(false);

  const results = [];

  try {
    for (const panel of panelsToExport) {
      const result = await exportPanel(page, panel, CONFIG.OUTPUT_DIR);
      results.push(result);
    }

    if (opts.includePanoramic) {
      const panoramicResult = await exportPanoramic(page, CONFIG.OUTPUT_DIR);
      results.push({ ...panoramicResult, name: 'Panoramic Preview' });
    }

  } finally {
    await browser.close();
  }

  // Summary
  const totalMs  = Date.now() - startMs;
  const succeeded = results.filter(r => r.success).length;
  const failed    = results.filter(r => !r.success).length;
  const totalBytes = results
    .filter(r => r.success && r.fileSize)
    .reduce((sum, r) => sum + r.fileSize, 0);

  console.log('\n' + '='.repeat(60));
  console.log('EXPORT SUMMARY');
  console.log('='.repeat(60));
  console.log(`Succeeded: ${succeeded} | Failed: ${failed}`);
  console.log(`Total output size: ${formatBytes(totalBytes)}`);
  console.log(`Total time: ${(totalMs / 1000).toFixed(1)}s`);

  if (succeeded > 0) {
    console.log('\nOutput files:');
    results.filter(r => r.success).forEach(r => {
      const badge = r.panel ? `P${r.panel}` : 'PR';
      console.log(`  [${badge}] ${r.outputFile} (${formatBytes(r.fileSize || 0)})`);
    });
  }

  if (failed > 0) {
    console.log('\nFailed panels:');
    results.filter(r => !r.success).forEach(r => {
      console.log(`  FAILED: ${r.error || 'Unknown error'}`);
    });
    process.exit(1);
  }

  console.log('\nNext step: run scripts/cmyk-convert.sh to convert to CMYK TIFF (Fogra39)');
  console.log('='.repeat(60));
}

main().catch(err => {
  console.error('\nFATAL ERROR:', err.message);
  console.error(err.stack);
  process.exit(1);
});
