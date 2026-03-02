# Panel 7 & 8 Redesign — Approved Design

Date: 2026-03-02
Status: APPROVED

---

## Panel 7: "Editorial Spread" — Credentials Wall

### Concept
Replace the 6 equally-weighted plaque cards with a magazine-editorial layout.
Three full-width editorial blocks, separated by thin copper rules.
Typography-driven — key stats become the visual element at massive scale.

### Zone A (top 783px)
- "Why Universal Metals" heading at 160px (down from 195px)
- Left-aligned or centered
- Logo top-right (existing pattern)

### Block 1: "Pakistan's Largest" (~2000px)
- **Hero**: `PAKISTAN'S LARGEST` at ~160px, copper-bold, left-aligned
- **Sub**: `PRODUCER OF` at ~72px, muted secondary, left-aligned
- **Product trio**: Three names horizontal, ~110px each:
  `COPPER ROD` | `ENAMELLED WIRE` | `PAPER COVERED STRIP`
  - Separated by thin vertical copper bars (no boxes)
  - Subtle copper underline accent under each
- **Ghost `01`**: Left margin (x=90px), ~300px, opacity 0.06

### Block 2: "Sustainability & Manufacturing" (~2000px)
- **Hero number**: `85%` at ~380px, copper-bold, right-aligned — visual centerpiece
- **Label**: `LESS CO₂` at ~72px beneath the number
- **Secondary stats** (left side, stacked vertically):
  - `100% RECYCLABLE` at ~96px
  - `3.9 TONNES CO₂ SAVED / TONNE` at ~72px
  - `2× PROPERZI CCR LINES` at ~72px
  - `5 NEWTECH ENAMELLING LINES` at ~72px
- **Context line**: `SUSTAINABLY PRODUCED FROM RECYCLED COPPER` at ~52px, muted, full-width bottom
- **Ghost `02`**: Left margin

### Block 3: "Certifications & Trade Advantage" (~1800px)
- **GSP+ accent band**: Full-width, ~400px tall, warm copper-tinted background (`rgba(245,184,128,0.08)`)
  - `GSP+ CERTIFIED` at ~130px, copper-bold
  - `ZERO EU IMPORT DUTY` at ~88px beneath
- **Cert seals row**: 4 stamps horizontal, ~280px each, copper ring borders
  - ISO 9001 (QUALITY) | ISO 14001 (ENVIRONMENTAL) | ISO 45001 (HEALTH & SAFETY) | CE Mark (EU CONFORMITY)
- **Ghost `03`**: Left margin

### Separators
- 3px horizontal copper rule (gradient fade) between each block
- No bordered cards anywhere

### Edge Stripe
- Left edge stripe stays (18px copper, marks left wall boundary)

---

## Panel 8: "Warm Copper Close" — Contact CTA

### Concept
Transform the flat white panel into a warm, premium-feeling close.
Subtle gradient background + brushed-metal texture + elevated card treatments.

### Background
- **Gradient**: Linear top-to-bottom
  - 0%: `#FFFFFF` (seamless with Panel 7)
  - 40%: `#FAF5EF` (warm cream)
  - 100%: `#F5ECD8` (champagne/light copper wash)
- **Texture overlay**: Subtle CSS noise/grain at ~4% opacity (inline SVG or base64 PNG tile)
  - Fine horizontal lines for brushed-metal impression

### Zone A (top 783px)
- Empty header (existing pattern, logo-only flex-end)

### Zone B: Brand Close + CTA (783px–3644px)
- **Logo**: 680px wide, centered
  - Add `drop-shadow(0 4px 32px rgba(139,74,40,0.08))`
- **"TALK TO US"**: 300px, copper-bold
  - Add `text-shadow: 0 2px 0 rgba(139,74,40,0.12)` (embossed/letterpress feel)
- **Copper underline**: Widen from 380px to 480px, increase opacity
- **Sub-line**: "About Your Copper Supply Chain" at 90px — no change needed

### Zone C: Contact Cards (3750px–6650px)
- **"Scan to save our contact"**: Bump to 60px (from 52px)
- **Contact cards** — frosted-glass treatment:
  - `background: rgba(255,255,255,0.7)`
  - `backdrop-filter: blur(8px)`
  - `border: 1px solid rgba(139,74,40,0.1)`
  - `box-shadow: 0 8px 48px rgba(139,74,40,0.08)`
  - QR codes remain dark/crisp inside
  - Print fallback: solid white + border still looks clean
- **Vertical separator**: Existing copper gradient (more presence on warm bg)
- **URL**: Bump to 100px (from 96px), full opacity (remove 0.85)

### Edge Stripe
- Right edge stripe stays (18px copper gradient, marks wall end)

### Print Export Notes
- CSS gradients export cleanly from Puppeteer
- Noise texture: use tiny inline SVG or base64 PNG — both Puppeteer-safe
- backdrop-filter may not render in Puppeteer — include solid fallback

---

## Content Unchanged
All credential text, certification data, contact info, and QR placeholders remain as-is.
This is a visual/layout redesign only.
