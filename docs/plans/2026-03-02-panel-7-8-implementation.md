# Panel 7 & 8 Redesign — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign Panel 7 ("Why Universal Metals") from plaque cards to an editorial magazine layout, and Panel 8 ("Talk to Us") from flat white to a warm copper gradient close.

**Architecture:** Each panel is a standalone HTML file + companion CSS file. Shared tokens live in `css/tokens.css`, shared layout in `css/layout.css`, shared components in `css/components.css`. Panel-specific overrides go in `css/panels/panel-N.css`. Export via Puppeteer at 3012x7441 CSS px (DSF 2).

**Tech Stack:** HTML5, CSS3 (custom properties from tokens.css), Puppeteer (export), Barlow Condensed + Poppins fonts (local woff2).

---

## Reference Files

Before starting ANY task, read these files to understand the design system:

- **Design tokens:** `css/tokens.css` — all color, type, spacing, and zone boundary variables
- **Layout system:** `css/layout.css` — panel container, zone positioning, utility classes
- **Components:** `css/components.css` — reusable headline, stat, badge, logo classes
- **Design spec:** `docs/plans/2026-03-02-panel-7-8-design.md` — approved design document

Key zone boundaries (from `tokens.css`):
- Zone A: 90px–783px (header, 693px tall)
- Zone B: 783px–3644px (hero, 2861px tall)
- Zone C: 3644px–5150px (info, 1506px tall) — panels override this to 3750px top, 2900px height
- Content inset: 90px from all edges
- Panel dimensions: 3012 × 7441 CSS px

---

### Task 1: Rewrite Panel 7 HTML — Editorial Structure

**Files:**
- Modify: `panels/panel-7.html` (complete rewrite of `<body>` content)

**Step 1: Read current panel-7.html**

Read `panels/panel-7.html` to understand the existing structure before replacing it.

**Step 2: Replace the HTML body**

Replace everything inside `<body>` with the new editorial 3-block structure:

```html
<main id="panel-7" class="panel panel--white" style="--panel-index: 6;">

  <div class="accent-bar accent-bar--top" role="presentation" aria-hidden="true"></div>
  <div class="edge-stripe edge-stripe--left" role="presentation" aria-hidden="true"></div>
  <div class="flow-svg-layer" aria-hidden="true"></div>

  <!-- ZONE A — Section Title -->
  <header class="zone-a" role="banner" aria-label="Panel header">
    <h2 class="p7-section-title">Why Universal Metals</h2>
  </header>

  <!-- EDITORIAL CONTENT — 3 blocks spanning zones B through D -->
  <div class="p7-editorial" role="region" aria-label="Company credentials">

    <!-- ═══ BLOCK 1: Pakistan's Largest ═══ -->
    <section class="p7-block p7-block--largest" aria-label="Pakistan's largest producer">
      <span class="p7-ghost" aria-hidden="true">01</span>
      <h3 class="p7-hero-line">Pakistan's Largest</h3>
      <p class="p7-sub-line">Producer of</p>
      <div class="p7-product-trio">
        <span class="p7-product-name">Copper Rod</span>
        <span class="p7-product-divider" role="presentation" aria-hidden="true"></span>
        <span class="p7-product-name">Enamelled Wire</span>
        <span class="p7-product-divider" role="presentation" aria-hidden="true"></span>
        <span class="p7-product-name">Paper Covered Strip</span>
      </div>
    </section>

    <!-- Copper rule separator -->
    <hr class="p7-rule" role="presentation" aria-hidden="true">

    <!-- ═══ BLOCK 2: Sustainability & Manufacturing ═══ -->
    <section class="p7-block p7-block--sustainability" aria-label="Sustainability and manufacturing credentials">
      <span class="p7-ghost" aria-hidden="true">02</span>
      <div class="p7-split">
        <div class="p7-split-left">
          <span class="p7-stat-line">100% Recyclable</span>
          <span class="p7-stat-line p7-stat-line--sm">3.9 Tonnes CO₂ Saved / Tonne</span>
          <span class="p7-stat-line p7-stat-line--sm">2× Properzi CCR Lines</span>
          <span class="p7-stat-line p7-stat-line--sm">5 Newtech Enamelling Lines</span>
        </div>
        <div class="p7-split-right">
          <span class="p7-hero-number">85<span class="p7-hero-percent">%</span></span>
          <span class="p7-hero-label">Less CO₂</span>
        </div>
      </div>
      <p class="p7-context-line">Sustainably Produced from Recycled Copper</p>
    </section>

    <!-- Copper rule separator -->
    <hr class="p7-rule" role="presentation" aria-hidden="true">

    <!-- ═══ BLOCK 3: Certifications & Trade Advantage ═══ -->
    <section class="p7-block p7-block--certs" aria-label="Certifications and trade advantage">
      <span class="p7-ghost" aria-hidden="true">03</span>

      <!-- GSP+ accent band -->
      <div class="p7-gsp-band">
        <span class="p7-gsp-title">GSP+ Certified</span>
        <span class="p7-gsp-sub">Zero EU Import Duty</span>
      </div>

      <!-- Certification seals row -->
      <div class="p7-seals-row">
        <div class="p7-seal">
          <img class="p7-seal-img" src="../assets/images/certs/ISO_9001.svg" alt="ISO 9001:2015">
          <span class="p7-seal-label">Quality</span>
        </div>
        <div class="p7-seal">
          <img class="p7-seal-img" src="../assets/images/certs/ISO_14001.svg" alt="ISO 14001:2015">
          <span class="p7-seal-label">Environmental</span>
        </div>
        <div class="p7-seal">
          <img class="p7-seal-img" src="../assets/images/certs/ISO_45001.svg" alt="ISO 45001:2018">
          <span class="p7-seal-label">Health & Safety</span>
        </div>
        <div class="p7-seal">
          <img class="p7-seal-img" src="../assets/images/certs/CE_Marking.svg" alt="CE Marking">
          <span class="p7-seal-label">EU Conformity</span>
        </div>
      </div>
    </section>

  </div>

  <div class="accent-bar accent-bar--bottom" role="presentation" aria-hidden="true"></div>

</main>
```

**Step 3: Verify HTML loads without errors**

Open `panels/panel-7.html` in the browser preview to check for broken references.

---

### Task 2: Rewrite Panel 7 CSS — Editorial Layout

**Files:**
- Modify: `css/panels/panel-7.css` (complete rewrite)

**Step 1: Read current panel-7.css**

Read `css/panels/panel-7.css` to understand existing patterns before replacing.

**Step 2: Write the new editorial CSS**

Replace the entire file with the new editorial layout styles:

```css
/*
 * panel-7.css — v7
 * Banner 7: Why Us — Editorial Spread | Universal Metals Pakistan Limited — CWIEME Berlin 2026
 *
 * Design concept: "Editorial Spread"
 *   Magazine-editorial layout with 3 full-width credential blocks.
 *   Typography-driven: key stats at massive scale ARE the visual element.
 *   Ghost watermark numbers in left margin like magazine page numbers.
 *   Thin copper rule separators between blocks.
 *
 * Zone A  — "WHY UNIVERSAL METALS" section title   (90px – 783px)
 * Editorial — 3 credential blocks                   (783px – 6650px)
 *
 * Left edge stripe: marks left wall boundary.
 */


/* ============================================================
   PANEL BACKGROUND
   ============================================================ */

#panel-7 {
  background: var(--bg-white);
}


/* ============================================================
   LEFT EDGE ACCENT STRIPE
   ============================================================ */

#panel-7 .edge-stripe--left {
  width: 18px;
  background: var(--copper-500);
}


/* ============================================================
   ZONE A — SECTION TITLE
   "Why Universal Metals" — restrained editorial title, not billboard.
   ============================================================ */

#panel-7 .zone-a {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 0;
}

#panel-7 .p7-section-title {
  font-family: var(--font-display);
  font-weight: var(--fw-bold);
  font-size: 160px;
  color: var(--text-copper-bold);
  text-transform: uppercase;
  letter-spacing: var(--ls-wide);
  line-height: var(--lh-heading);
  text-rendering: geometricPrecision;
}


/* ============================================================
   EDITORIAL CONTAINER
   Spans from zone-b top (783px) to near panel bottom (~6650px).
   Three blocks stacked vertically with copper rules between.
   ============================================================ */

#panel-7 .p7-editorial {
  position: absolute;
  top: 783px;
  left: var(--content-inset);
  right: var(--content-inset);
  height: 5867px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  justify-content: stretch;
  padding: 80px 0;
}


/* ============================================================
   EDITORIAL BLOCK — shared base
   ============================================================ */

#panel-7 .p7-block {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px 40px;
}


/* ============================================================
   COPPER RULE SEPARATOR
   ============================================================ */

#panel-7 .p7-rule {
  width: 100%;
  height: 3px;
  border: none;
  flex-shrink: 0;
  background: linear-gradient(
    to right,
    transparent 0%,
    var(--copper-300) 10%,
    var(--copper-500) 50%,
    var(--copper-300) 90%,
    transparent 100%
  );
}


/* ============================================================
   GHOST WATERMARK NUMBERS
   Left-margin page numbers at very low opacity.
   ============================================================ */

#panel-7 .p7-ghost {
  position: absolute;
  left: -10px;
  top: 50%;
  transform: translateY(-50%);
  font-family: var(--font-display);
  font-weight: var(--fw-extrabold);
  font-size: 340px;
  line-height: 1;
  color: var(--copper-500);
  opacity: 0.06;
  pointer-events: none;
  user-select: none;
  letter-spacing: -0.02em;
}


/* ============================================================
   BLOCK 1 — PAKISTAN'S LARGEST
   ============================================================ */

#panel-7 .p7-hero-line {
  font-family: var(--font-display);
  font-weight: var(--fw-bold);
  font-size: 160px;
  color: var(--text-copper-bold);
  text-transform: uppercase;
  letter-spacing: var(--ls-wide);
  line-height: 1.0;
  text-rendering: geometricPrecision;
}

#panel-7 .p7-sub-line {
  font-family: var(--font-display);
  font-weight: var(--fw-medium);
  font-size: 72px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: var(--ls-wider);
  line-height: 1.2;
  margin-top: 16px;
}

/* Product trio — horizontal row with vertical copper dividers */
#panel-7 .p7-product-trio {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  gap: 0;
  margin-top: 60px;
  width: 100%;
}

#panel-7 .p7-product-name {
  flex: 1;
  font-family: var(--font-display);
  font-weight: var(--fw-bold);
  font-size: 100px;
  color: var(--text-copper-bold);
  text-transform: uppercase;
  letter-spacing: var(--ls-wide);
  line-height: 1.06;
  text-align: center;
  text-rendering: geometricPrecision;
  padding: 40px 20px;
  position: relative;
}

/* Copper underline accent under each product name */
#panel-7 .p7-product-name::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 4px;
  background: linear-gradient(
    to right,
    transparent 0%,
    var(--copper-300) 20%,
    var(--copper-500) 50%,
    var(--copper-300) 80%,
    transparent 100%
  );
  border-radius: 2px;
}

/* Vertical copper divider between product names */
#panel-7 .p7-product-divider {
  width: 3px;
  align-self: stretch;
  flex-shrink: 0;
  background: linear-gradient(
    to bottom,
    transparent 0%,
    var(--copper-300) 20%,
    var(--copper-500) 50%,
    var(--copper-300) 80%,
    transparent 100%
  );
  border-radius: 2px;
}


/* ============================================================
   BLOCK 2 — SUSTAINABILITY & MANUFACTURING
   Split layout: stats left, hero "85%" number right.
   ============================================================ */

#panel-7 .p7-split {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  gap: 80px;
}

#panel-7 .p7-split-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

#panel-7 .p7-split-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
}

/* Stat lines on the left */
#panel-7 .p7-stat-line {
  font-family: var(--font-display);
  font-weight: var(--fw-bold);
  font-size: 96px;
  color: var(--text-copper-bold);
  text-transform: uppercase;
  letter-spacing: var(--ls-wide);
  line-height: 1.1;
  text-rendering: geometricPrecision;
}

#panel-7 .p7-stat-line--sm {
  font-size: 72px;
  font-weight: var(--fw-semibold);
  color: var(--text-secondary);
}

/* Hero number on the right */
#panel-7 .p7-hero-number {
  font-family: var(--font-display);
  font-weight: var(--fw-extrabold);
  font-size: 380px;
  color: var(--text-copper-bold);
  letter-spacing: -0.03em;
  line-height: 0.85;
  text-rendering: geometricPrecision;
}

#panel-7 .p7-hero-percent {
  font-size: 200px;
  font-weight: var(--fw-bold);
  color: var(--copper-500);
  vertical-align: super;
  line-height: 1;
}

#panel-7 .p7-hero-label {
  font-family: var(--font-display);
  font-weight: var(--fw-bold);
  font-size: 96px;
  color: var(--copper-500);
  text-transform: uppercase;
  letter-spacing: var(--ls-wide);
  line-height: 1.1;
  text-rendering: geometricPrecision;
  margin-top: 16px;
}

/* Context line spanning full width at bottom of block */
#panel-7 .p7-context-line {
  font-family: var(--font-display);
  font-weight: var(--fw-medium);
  font-size: 52px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: var(--ls-wider);
  line-height: 1.2;
  margin-top: 48px;
  text-rendering: geometricPrecision;
}


/* ============================================================
   BLOCK 3 — CERTIFICATIONS & TRADE ADVANTAGE
   ============================================================ */

/* GSP+ accent band */
#panel-7 .p7-gsp-band {
  width: 100%;
  background: rgba(245, 184, 128, 0.08);
  padding: 80px 60px;
  text-align: center;
  margin-bottom: 60px;
}

#panel-7 .p7-gsp-title {
  display: block;
  font-family: var(--font-display);
  font-weight: var(--fw-bold);
  font-size: 130px;
  color: var(--text-copper-bold);
  text-transform: uppercase;
  letter-spacing: var(--ls-wide);
  line-height: 1.05;
  text-rendering: geometricPrecision;
}

#panel-7 .p7-gsp-sub {
  display: block;
  font-family: var(--font-display);
  font-weight: var(--fw-semibold);
  font-size: 88px;
  color: var(--copper-500);
  text-transform: uppercase;
  letter-spacing: var(--ls-wide);
  line-height: 1.1;
  margin-top: 16px;
  text-rendering: geometricPrecision;
}

/* Certification seals row */
#panel-7 .p7-seals-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: flex-start;
  gap: 60px;
  width: 100%;
}

#panel-7 .p7-seal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  flex: 1;
  max-width: 400px;
}

#panel-7 .p7-seal-img {
  display: block;
  width: 280px;
  height: 280px;
  object-fit: contain;
  border: 4px solid var(--copper-300);
  border-radius: 50%;
  padding: 20px;
  background: var(--bg-white);
}

#panel-7 .p7-seal-label {
  font-family: var(--font-display);
  font-weight: var(--fw-semibold);
  font-size: 52px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: var(--ls-wide);
  text-align: center;
  text-rendering: geometricPrecision;
}
```

**Step 3: Open in browser and visually verify layout**

Open `panels/panel-7.html` in browser. Check:
- Zone A heading visible and left-aligned
- Three blocks fill the vertical space evenly
- Ghost numbers visible in left margin at low opacity
- Copper rules between blocks
- Product names in Block 1 are horizontal with dividers
- "85%" dominates Block 2 right side
- GSP+ band has warm tinted background in Block 3
- Cert seals render as circles in a row

**Step 4: Export panel 7 PNG**

Run: `cd /Users/ibrahimkashif/Desktop/CWEIME/UM_Banners && node scripts/export.js --panel 7`

Expected: PNG at `output/png/panel-7.png` (6024 × 14882 px)

**Step 5: Visually verify the exported PNG**

Read the exported PNG file and check the overall composition, typography scale, and spacing.

---

### Task 3: Iterate on Panel 7 spacing and typography

**Files:**
- Modify: `css/panels/panel-7.css` (fine-tune values)
- Possibly: `panels/panel-7.html` (minor structural tweaks)

After seeing the first export, adjustments will likely be needed for:
- Block vertical distribution (flex proportions may need adjustment)
- Ghost number positioning and size
- Product trio font sizes (may need to shrink for "Paper Covered Strip")
- Hero "85%" scale relative to the block height
- GSP+ band padding and margin
- Seal sizes and spacing

**Step 1: Identify issues from the PNG export**

Look at `output/png/panel-7.png` and note specific problems.

**Step 2: Adjust CSS values**

Apply targeted fixes to `css/panels/panel-7.css`. Common adjustments:
- `flex` ratios on `.p7-block` to rebalance vertical space
- Font sizes if text overflows or looks too small
- `gap` and `margin` values for breathing room

**Step 3: Re-export and verify**

Run: `cd /Users/ibrahimkashif/Desktop/CWEIME/UM_Banners && node scripts/export.js --panel 7`

Repeat until the layout matches the design spec.

---

### Task 4: Update Panel 8 CSS — Warm Copper Close

**Files:**
- Modify: `css/panels/panel-8.css` (targeted CSS updates, not full rewrite)

Panel 8's HTML structure stays the same. Changes are CSS-only.

**Step 1: Read current panel-8.css**

Read `css/panels/panel-8.css` to understand existing styles.

**Step 2: Add warm gradient background**

Change the `#panel-8` background from flat white to a warm vertical gradient:

```css
#panel-8 {
  background: linear-gradient(
    to bottom,
    #FFFFFF 0%,
    #FAF5EF 40%,
    #F5ECD8 100%
  );
}
```

**Step 3: Increase noise texture opacity for Panel 8**

Add a panel-specific override to make the existing noise texture slightly more visible:

```css
#panel-8.panel::before {
  opacity: 0.05;
}
```

**Step 4: Add logo drop shadow**

```css
#panel-8 .p8-logo {
  display: block;
  width: 680px;
  height: auto;
  filter: drop-shadow(0 4px 32px rgba(139, 74, 40, 0.08));
}
```

**Step 5: Add embossed text effect to CTA heading**

```css
#panel-8 .p8-cta-heading {
  /* ... existing properties stay ... */
  text-shadow: 0 2px 0 rgba(139, 74, 40, 0.12);
}
```

**Step 6: Widen the copper underline**

Update `.p8-cta-heading::after` width from 380px to 480px.

**Step 7: Add frosted glass to contact cards**

```css
#panel-8 .p8-card {
  /* ... existing properties stay ... */
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(139, 74, 40, 0.1);
  border-radius: 16px;
  box-shadow: 0 8px 48px rgba(139, 74, 40, 0.08);
  padding: 60px 80px;
}
```

**Step 8: Bump scan label and URL sizes**

Update `.p8-scan-label` font-size from 52px to 60px.
Update `.p8-url` font-size from 96px to 100px and remove `opacity: 0.85`.

**Step 9: Export and verify**

Run: `cd /Users/ibrahimkashif/Desktop/CWEIME/UM_Banners && node scripts/export.js --panel 8`

Check:
- Warm gradient visible from white to champagne
- Logo has subtle shadow lift
- "TALK TO US" has embossed feel
- Contact cards have frosted glass appearance (or clean white fallback)
- URL at full opacity

---

### Task 5: Iterate on Panel 8 warmth and balance

**Files:**
- Modify: `css/panels/panel-8.css` (fine-tune gradient, shadows, spacing)

**Step 1: Check gradient strength in export**

The gradient may be too subtle or too strong in the PNG. Adjust the color stops:
- If too subtle: push `#F5ECD8` endpoint closer to `#EED9BF`
- If too strong: soften to `#FAF0E4`

**Step 2: Check backdrop-filter rendering**

Puppeteer may not render `backdrop-filter`. If the frosted glass doesn't appear, add a solid fallback:

```css
/* Fallback for Puppeteer which may not support backdrop-filter */
@supports not (backdrop-filter: blur(8px)) {
  #panel-8 .p8-card {
    background: rgba(255, 255, 255, 0.92);
  }
}
```

Or simply set a solid background that approximates the frosted look.

**Step 3: Re-export both panels**

Run: `cd /Users/ibrahimkashif/Desktop/CWEIME/UM_Banners && node scripts/export.js --panel 7 && node scripts/export.js --panel 8`

Verify both panels look complete and cohesive.

---

### Task 6: Final verification and cleanup

**Files:**
- Check: `output/png/panel-7.png`, `output/png/panel-8.png`
- Cleanup: delete `panels/panel-7-card-options.html` if no longer needed (confirm with user)

**Step 1: Side-by-side comparison**

Export panels 6, 7, and 8 together:
```bash
cd /Users/ibrahimkashif/Desktop/CWEIME/UM_Banners
node scripts/export.js --panel 6
node scripts/export.js --panel 7
node scripts/export.js --panel 8
```

Verify visual flow: Panel 6 (products) → Panel 7 (credentials, editorial) → Panel 8 (warm CTA close).

**Step 2: Check print safety**

Verify in the exported PNGs:
- No text below 0.80 opacity (except ghosts/decorative elements)
- All copper text colors meet contrast requirements (copper-700 = 6.76:1 on white)
- Gradient background doesn't cause banding (noise texture should prevent this)
- Cert seal SVGs render correctly

**Step 3: Document changes**

No new docs needed — the design doc at `docs/plans/2026-03-02-panel-7-8-design.md` serves as the record.
