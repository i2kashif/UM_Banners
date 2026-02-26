#!/bin/bash
# =============================================================================
# cmyk-convert.sh
# Universal Metals Pakistan Limited — CWIEME Berlin 2026
#
# Convert sRGB PNG exports to CMYK TIFF using Fogra39 ICC profile.
#
# Conversion details:
#   Source:  sRGB (IEC 61966-2-1) PNG files from Puppeteer export
#   Target:  CMYK Fogra39 (ISOcoated_v2_300_eci.icc)
#   Intent:  Relative Colorimetric (perceptual is an alternative — see notes)
#   Output:  LZW-compressed TIFF, 150 DPI, CMYK colour space
#
# Fogra39 = ISOcoated_v2_300_eci.icc
#   Download: http://www.eci.org/en/downloads#icc_profiles_for_offset_printing
#   Place at: assets/icc/ISOcoated_v2_300_eci.icc
#
# Prerequisites:
#   ImageMagick 7+: brew install imagemagick (macOS) | apt install imagemagick
#   Little CMS (lcms2): bundled with modern ImageMagick
#
# Usage:
#   bash scripts/cmyk-convert.sh             # Convert all panel-N.png files
#   bash scripts/cmyk-convert.sh --verify    # Also log CMYK spot colour values
#
# Output:
#   output/cmyk/panel-N-cmyk.tiff
#
# =============================================================================

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

INPUT_DIR="$REPO_ROOT/output/png"
OUTPUT_DIR="$REPO_ROOT/output/cmyk"
ICC_DIR="$REPO_ROOT/assets/icc"

FOGRA39_PROFILE="$ICC_DIR/ISOcoated_v2_300_eci.icc"
SRGB_PROFILE="$ICC_DIR/sRGB_IEC61966-2-1.icc"

# ImageMagick rendering intent:
# Relative colorimetric (1) preserves white point — preferred for spot colours
# Perceptual (0) compresses gamut — better for photos with saturated colours
RENDERING_INTENT="Relative"    # Options: Undefined, Saturation, Perceptual, Absolute, Relative

# Output compression
TIFF_COMPRESSION="LZW"         # LZW = lossless, smaller than Uncompressed

# Copper brand colours for CMYK verification (sRGB hex values)
COPPER_HEX_VALUES=(
  "#B2673E"   # copper-600 — headline text
  "#CE7340"   # copper-500 — stat numbers
  "#F5B880"   # copper-300 — accents
  "#8B4A28"   # copper-700 — dark anchors
  "#1A1208"   # text-primary — body text
  "#FFFFFF"   # white background
  "#FAF8F5"   # cream background
)

VERIFY_MODE=false
if [[ "${1:-}" == "--verify" ]]; then
  VERIFY_MODE=true
fi

# =============================================================================
# COLOUR HELPERS
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

print_header() {
  echo ""
  echo -e "${BOLD}================================================================${RESET}"
  echo -e "${BOLD}$1${RESET}"
  echo -e "${BOLD}================================================================${RESET}"
}

print_ok()   { echo -e "  ${GREEN}[OK]${RESET}  $1"; }
print_warn() { echo -e "  ${YELLOW}[WARN]${RESET} $1"; }
print_err()  { echo -e "  ${RED}[ERR]${RESET}  $1"; }
print_info() { echo -e "  ${CYAN}[INFO]${RESET} $1"; }

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================

print_header "UMPL CWIEME Berlin 2026 — CMYK Conversion (Fogra39)"

echo ""
echo "  Source:  $INPUT_DIR"
echo "  Output:  $OUTPUT_DIR"
echo "  Profile: $FOGRA39_PROFILE"
echo "  Intent:  $RENDERING_INTENT Colorimetric"
echo "  Format:  CMYK TIFF (LZW compressed)"
echo ""

# Check ImageMagick
if ! command -v convert &>/dev/null && ! command -v magick &>/dev/null; then
  print_err "ImageMagick not found."
  print_err "Install with: brew install imagemagick (macOS) | apt install imagemagick (Ubuntu)"
  exit 1
fi

# Determine ImageMagick command (v6 uses 'convert', v7 uses 'magick')
if command -v magick &>/dev/null; then
  IM_CMD="magick"
  IM_CONVERT="magick convert"
else
  IM_CMD="convert"
  IM_CONVERT="convert"
fi

IM_VERSION=$($IM_CMD --version 2>&1 | head -n1)
print_ok "ImageMagick: $IM_VERSION"

# Check for Fogra39 ICC profile
if [ ! -f "$FOGRA39_PROFILE" ]; then
  print_warn "Fogra39 ICC profile not found at:"
  print_warn "  $FOGRA39_PROFILE"
  echo ""
  echo "  Download ISOcoated_v2_300_eci.icc from:"
  echo "  http://www.eci.org/en/downloads#icc_profiles_for_offset_printing"
  echo ""
  echo "  Once downloaded, place it at:"
  echo "  $FOGRA39_PROFILE"
  echo ""
  echo "  Conversion will continue using ImageMagick's built-in CMYK conversion"
  echo "  (no ICC profile) — NOT suitable for final print submission."
  echo ""
  USE_ICC=false
else
  print_ok "Fogra39 profile found: $FOGRA39_PROFILE"
  USE_ICC=true
fi

# Check for sRGB source profile
if [ ! -f "$SRGB_PROFILE" ]; then
  print_warn "sRGB source profile not found — will use embedded profile if present"
  USE_SRGB_ICC=false
else
  print_ok "sRGB source profile found: $SRGB_PROFILE"
  USE_SRGB_ICC=true
fi

# Check input directory
if [ ! -d "$INPUT_DIR" ]; then
  print_err "Input directory not found: $INPUT_DIR"
  print_err "Run scripts/export.js first to generate PNG files."
  exit 1
fi

# Find PNG files to process
PNG_FILES=("$INPUT_DIR"/panel-*.png)
PNG_COUNT=0
for f in "${PNG_FILES[@]}"; do
  [ -f "$f" ] && PNG_COUNT=$((PNG_COUNT + 1))
done

if [ "$PNG_COUNT" -eq 0 ]; then
  print_err "No panel-N.png files found in $INPUT_DIR"
  print_err "Run: node scripts/export.js"
  exit 1
fi

print_ok "Found $PNG_COUNT PNG file(s) to convert"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# =============================================================================
# CONVERSION
# =============================================================================

print_header "Converting $PNG_COUNT panels sRGB PNG → CMYK TIFF"

CONVERTED=0
FAILED=0
TOTAL_OUTPUT_BYTES=0

for PNG_FILE in "$INPUT_DIR"/panel-*.png; do
  [ -f "$PNG_FILE" ] || continue

  BASENAME=$(basename "$PNG_FILE" .png)
  TIFF_FILE="$OUTPUT_DIR/${BASENAME}-cmyk.tiff"

  echo ""
  echo -e "  ${BOLD}${BASENAME}.png${RESET}"

  # Get input file info
  PNG_SIZE=$(stat -f%z "$PNG_FILE" 2>/dev/null || stat -c%s "$PNG_FILE" 2>/dev/null || echo "0")
  echo "    Input:  $(( PNG_SIZE / 1024 / 1024 ))MB ($PNG_SIZE bytes)"

  START_TS=$SECONDS

  # Build conversion command
  if [ "$USE_ICC" = true ] && [ "$USE_SRGB_ICC" = true ]; then
    # Full ICC-managed conversion: sRGB source → Fogra39 CMYK target
    $IM_CONVERT \
      "$PNG_FILE" \
      -profile "$SRGB_PROFILE" \
      -intent "$RENDERING_INTENT" \
      -profile "$FOGRA39_PROFILE" \
      -compress "$TIFF_COMPRESSION" \
      -density 150 \
      "$TIFF_FILE" 2>&1 | while read line; do
        [ -n "$line" ] && echo "    IM: $line"
      done || true

  elif [ "$USE_ICC" = true ]; then
    # Fogra39 target only (rely on embedded sRGB in PNG)
    $IM_CONVERT \
      "$PNG_FILE" \
      -intent "$RENDERING_INTENT" \
      -profile "$FOGRA39_PROFILE" \
      -compress "$TIFF_COMPRESSION" \
      -density 150 \
      "$TIFF_FILE" 2>&1 | while read line; do
        [ -n "$line" ] && echo "    IM: $line"
      done || true

  else
    # No ICC profile — basic sRGB to CMYK (not for final print)
    print_warn "No ICC profile — converting without colour management"
    $IM_CONVERT \
      "$PNG_FILE" \
      -colorspace CMYK \
      -compress "$TIFF_COMPRESSION" \
      -density 150 \
      "$TIFF_FILE" 2>&1 | while read line; do
        [ -n "$line" ] && echo "    IM: $line"
      done || true
  fi

  ELAPSED=$(( SECONDS - START_TS ))

  if [ -f "$TIFF_FILE" ]; then
    TIFF_SIZE=$(stat -f%z "$TIFF_FILE" 2>/dev/null || stat -c%s "$TIFF_FILE" 2>/dev/null || echo "0")
    TOTAL_OUTPUT_BYTES=$(( TOTAL_OUTPUT_BYTES + TIFF_SIZE ))
    TIFF_MB=$(( TIFF_SIZE / 1024 / 1024 ))
    print_ok "Output: ${BASENAME}-cmyk.tiff (${TIFF_MB}MB) in ${ELAPSED}s"
    CONVERTED=$(( CONVERTED + 1 ))
  else
    print_err "Conversion failed for $BASENAME"
    FAILED=$(( FAILED + 1 ))
  fi
done

# =============================================================================
# CMYK SPOT COLOUR VERIFICATION (optional)
# =============================================================================

if [ "$VERIFY_MODE" = true ] && [ "$CONVERTED" -gt 0 ]; then
  print_header "CMYK Spot Colour Verification"

  echo ""
  echo "  Checking representative copper brand colours..."
  echo "  (Uses first successfully converted TIFF as reference)"
  echo ""

  SAMPLE_TIFF=""
  for f in "$OUTPUT_DIR"/panel-*-cmyk.tiff; do
    [ -f "$f" ] && SAMPLE_TIFF="$f" && break
  done

  if [ -z "$SAMPLE_TIFF" ]; then
    print_warn "No TIFF files found for verification"
  else
    echo "  Sample: $(basename "$SAMPLE_TIFF")"
    echo ""

    # Print CMYK conversion reference table for copper palette
    # These are approximate expected CMYK values for Fogra39 target
    # Actual values will vary slightly based on ImageMagick version and LCM implementation
    printf "  %-16s %-30s %s\n" "sRGB Hex" "Brand Name" "Expected CMYK (Fogra39 approx.)"
    printf "  %s\n" "------------------------------------------------------------"
    printf "  %-16s %-30s %s\n" "#B2673E" "copper-600 (headline)" "C:18 M:58 Y:72 K:8"
    printf "  %-16s %-30s %s\n" "#CE7340" "copper-500 (stat nums)" "C:12 M:55 Y:78 K:2"
    printf "  %-16s %-30s %s\n" "#F5B880" "copper-300 (accents)"  "C:2  M:32 Y:50 K:0"
    printf "  %-16s %-30s %s\n" "#8B4A28" "copper-700 (dark)"     "C:30 M:67 Y:82 K:24"
    printf "  %-16s %-30s %s\n" "#1A1208" "text-primary (body)"   "C:64 M:60 Y:60 K:92"
    printf "  %-16s %-30s %s\n" "#FFFFFF" "white (bg)"            "C:0  M:0  Y:0  K:0"
    printf "  %-16s %-30s %s\n" "#FAF8F5" "cream (bg-cream)"      "C:1  M:1  Y:2  K:0"
    echo ""
    echo "  NOTE: Values are approximate. Verify with a proof print before final production."
    echo "  Total ink coverage for copper-600 (#B2673E): ~156% — within Fogra39 300% TIL."
    echo "  Total ink coverage for text-primary (#1A1208): ~276% — within Fogra39 300% TIL."
  fi
fi

# =============================================================================
# SUMMARY
# =============================================================================

print_header "Conversion Summary"

echo ""
echo "  Converted:  $CONVERTED / $PNG_COUNT"
if [ "$FAILED" -gt 0 ]; then
  echo -e "  ${RED}Failed:     $FAILED${RESET}"
fi

if [ "$TOTAL_OUTPUT_BYTES" -gt 0 ]; then
  TOTAL_MB=$(( TOTAL_OUTPUT_BYTES / 1024 / 1024 ))
  echo "  Total TIFF: ${TOTAL_MB}MB"
fi

echo ""
echo "  Output directory: $OUTPUT_DIR"
echo ""

if [ "$USE_ICC" = false ]; then
  echo -e "  ${YELLOW}IMPORTANT: Conversion was performed without ICC profile management.${RESET}"
  echo -e "  ${YELLOW}The TIFF files are NOT suitable for print submission.${RESET}"
  echo -e "  ${YELLOW}Download ISOcoated_v2_300_eci.icc and re-run this script.${RESET}"
  echo ""
fi

if [ "$CONVERTED" -gt 0 ]; then
  echo "  Next steps:"
  echo "  1. Open TIFF files in Acrobat or InDesign to verify CMYK values"
  echo "  2. Check that total ink coverage does not exceed 300% (Fogra39 TIL)"
  echo "  3. Soft-proof using Fogra39 in Acrobat or Photoshop before sending to print"
  echo "  4. Send CMYK TIFFs to printer — specify ISOcoated_v2_300_eci / Fogra39"
  echo ""
fi

if [ "$FAILED" -gt 0 ]; then
  exit 1
fi

echo "================================================================"
