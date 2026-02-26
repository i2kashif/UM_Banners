"""
generate_images.py
==================
AI Image Generation Script for CWIEME Berlin 2026 Trade Show Banners
Universal Metals Pakistan Limited

Uses Nano Banana Pro (Gemini 3 Pro Image Preview) via the google-genai SDK.
Generates professional product images for 8-banner trade show system.

Usage:
    python3 generate_images.py
    python3 generate_images.py --force   # regenerate all, overwriting existing

API Key: GEMINI_API_KEY environment variable (required)
Output:  ../assets/images/generated/
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime

# ── SDK import (new google-genai preferred; fall back to legacy google-generativeai)
try:
    from google import genai
    from google.genai import types
    USE_NEW_SDK = True
    print("[SDK] Using google-genai (new SDK)")
except ImportError:
    import google.generativeai as genai_legacy
    USE_NEW_SDK = False
    print("[SDK] Falling back to google-generativeai (legacy SDK)")

from PIL import Image
import io

# ── Configuration
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable is not set.")
    sys.exit(1)

SCRIPT_DIR  = Path(__file__).parent.resolve()
OUTPUT_DIR  = (SCRIPT_DIR / ".." / "assets" / "images" / "generated").resolve()
REF_DIR     = Path("/Users/ibrahimkashif/Desktop/CWEIME/Marketing_Info/images copy/products")
LOG_FILE    = OUTPUT_DIR / "generation_log.json"

# Primary model (Nano Banana Pro)
PRIMARY_MODEL = "gemini-3-pro-image-preview"
# Fallback model if primary fails
FALLBACK_MODEL = "gemini-2.0-flash-exp-image-generation"

DELAY_BETWEEN_REQUESTS = 8   # seconds — avoids rate limiting
MAX_RETRIES = 3
RETRY_WAIT  = 15             # seconds between retries on rate-limit errors

# ── Style prefix (from Phase1_Image_Prompt_Engineer_Prompts.md)
STYLE_PREFIX = (
    "Warm-toned professional product photography aesthetic. "
    "Background is pure white (#FFFFFF) or warm cream (#FAF8F5). "
    "Lighting is a premium three-point softbox studio setup with a dominant warm key light "
    "from camera left at 45 degrees, emphasizing copper and amber tones. "
    "The overall feel is modern industrial premium — think Siemens or ABB product catalogue, "
    "not warehouse photography. Photorealistic, sharp focus, high resolution suitable for "
    "large-format print."
)

# ══════════════════════════════════════════════════════════════════════════════
# PROMPTS  (verbatim from Phase1_Image_Prompt_Engineer_Prompts.md)
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {

    # ── Banner 3: Copper Enamelled Wire (HERO product) ────────────────────────
    "banner3_enamelled_wire_optA": {
        "filename": "banner3_enamelled_wire_optA.png",
        "reference": "enamelled-wire/Copper_Enamelled_Wire.jpeg",
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Use the uploaded product photograph as the subject reference. "
            "The image shows a large industrial spool of copper enamelled magnet wire with black "
            "plastic flanges and tightly wound warm amber-copper wire. I need this same product "
            "re-photographed in a more premium, elevated style.\n\n"
            "Generate a photorealistic studio hero photograph of this copper enamelled wire spool. "
            "The spool should be positioned at a slight 15-degree rotation from dead-center, showing "
            "the face and a hint of depth on the side. Place it on a pure white background (#FFFFFF) "
            "with a very faint warm cream gradient at the base. Use a premium three-point softbox "
            "lighting setup: a warm key light from camera left at 45 degrees creating a golden "
            "highlight band across the wire surface, a soft fill light from camera right at lower "
            "intensity, and a subtle hair light from above-behind creating a fine rim glow on the "
            "top flange.\n\n"
            "The copper wire should appear luminous — each strand catching the warm light "
            "individually, creating a rich textural surface with visible micro-detail in the winding "
            "pattern. The amber-copper color (#E8A065 to #F5B880 tonal range) should be the dominant "
            "visual element. The black plastic flanges should appear as clean, professional matte "
            "elements that frame the copper without competing with it.\n\n"
            "Shoot with an 85mm portrait lens at f/2.8 for a slight background fade, but the entire "
            "spool should remain in sharp focus. The spool should fill approximately 75% of the "
            "frame height. Subtle soft shadow beneath the spool for natural grounding. "
            "No text, no logos, no props.\n\n"
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 3 — Copper Enamelled Wire (HERO)",
        "option": "A (with reference image)",
    },

    "banner3_enamelled_wire_optB": {
        "filename": "banner3_enamelled_wire_optB.png",
        "reference": None,
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Generate a photorealistic premium studio hero photograph of a large industrial copper "
            "enamelled magnet wire spool. The spool has matte black industrial plastic flanges "
            "(top and bottom discs) and is densely wound with fine copper enamelled wire — the wire "
            "surface appears as a rich, warm amber-copper texture with individual strands visible "
            "across the face of the spool. The wire color ranges from deep copper-brown in shadow "
            "areas (#CE7340) to glowing amber-gold in lit areas (#F5B880), creating a rich tonal "
            "depth across the cylindrical face.\n\n"
            "Composition: The spool is centered in the frame, filling approximately 75% of the "
            "image height, positioned at a slight 15-degree rotation to show dimensionality. "
            "Shot with an 85mm lens at f/2.8. Pure white background (#FFFFFF) with barely "
            "perceptible warm cream gradient at the very base.\n\n"
            "Lighting: Premium three-point studio softbox setup. Warm key light from camera left "
            "at 45 degrees illuminating the wire surface with golden warmth. Softer fill from "
            "camera right. Gentle rim light from above-rear creating a highlight on the upper "
            "flange edge. The lighting makes the copper wire appear luminous and warm — each "
            "strand catches light individually.\n\n"
            "The overall impression should be that of a premium catalogue photograph for a "
            "world-class manufacturer. Think Siemens or ABB product photography — clean, "
            "authoritative, warm, and precise.\n\n"
            "No text, no logos, no props, no people. "
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 3 — Copper Enamelled Wire (HERO)",
        "option": "B (text-only)",
    },

    # ── Banner 4: Paper Covered Copper Strip ─────────────────────────────────
    "banner4_paper_strip_optA": {
        "filename": "banner4_paper_strip_optA.png",
        "reference": "insulation/Paper_Covered_Copper_Strip.jpg",
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Use the uploaded product photograph as the subject reference. The image shows a large "
            "spool of paper-covered copper strip with distinctive tan/kraft paper wrapping creating "
            "a fine striped texture across the face of the spool. The spool has matte black "
            "industrial flanges.\n\n"
            "I need this product re-photographed on a clean studio background — replace the grey "
            "concrete floor with a pure white (#FFFFFF) or very warm cream (#FAF8F5) background. "
            "Keep the spool in exactly the same front-facing composition.\n\n"
            "Apply premium studio lighting: a warm key light from camera left at 45 degrees that "
            "reveals the subtle texture of the kraft paper surface and makes the warm tan color "
            "glow slightly. The paper strips should show clear definition — each strip visible, "
            "showing the precision of the winding. The black flanges should remain as clean "
            "professional frames. Add a gentle fill light from camera right to illuminate the "
            "shadow side without losing contrast. Soft, warm shadow beneath the spool for grounding.\n\n"
            "The tan/kraft paper color should appear warm and natural — not bleached, not flat. "
            "Think of the color of premium archival paper in warm light: a rich, earthy tan with "
            "gentle warmth.\n\n"
            "Shot from a slightly elevated 10-degree angle looking down at the spool face. "
            "50mm lens at f/5.6 for full spool sharpness. The spool should fill 80% of the frame. "
            "No text, no logos.\n\n"
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 4 — Paper Covered Copper Strip",
        "option": "A (with reference image)",
    },

    "banner4_paper_strip_optB": {
        "filename": "banner4_paper_strip_optB.png",
        "reference": None,
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Generate a photorealistic premium studio product photograph of a large industrial "
            "spool of paper-covered copper strip (PCCS — paper covered copper strip for "
            "transformer windings).\n\n"
            "The product: A heavy industrial spool with matte black plastic flanges. The face of "
            "the spool is covered in tightly wound flat copper strips, each individually wrapped "
            "in tan/kraft paper insulation. The surface texture is a precise, rhythmic pattern of "
            "horizontal kraft-paper-wrapped strips — like a cross-section of a book, viewed from "
            "the spine. The color is warm natural tan (#D4A976 range) with subtle variation between "
            "individual strips where the edges catch light differently. The winding is perfectly "
            "even, suggesting precision manufacturing.\n\n"
            "At the edge of the spool, a hint of the inner copper strip should be faintly visible "
            "where the paper starts — suggesting the material beneath.\n\n"
            "Composition: Spool centered, filling 80% of the frame. Front-facing with a very "
            "slight 10-degree rotation to show depth. 50mm lens at f/5.6 for uniform sharpness "
            "across the entire surface. Pure white (#FFFFFF) to warm cream (#FAF8F5) background.\n\n"
            "Lighting: Warm key light from camera left revealing the paper texture with gentle "
            "shadow between each strip. Soft fill from camera right. The paper surface should look "
            "like premium kraft paper — warm, textured, not glossy. The overall image communicates "
            "precision craftsmanship.\n\n"
            "No text, no logos, no props. "
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 4 — Paper Covered Copper Strip",
        "option": "B (text-only)",
    },

    # ── Banner 5: CCR Copper Rod ──────────────────────────────────────────────
    "banner5_copper_rod_optA": {
        "filename": "banner5_copper_rod_optA.png",
        "reference": "rods/CCR_Rod_Image_1.png",
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Use the uploaded product image as the primary subject reference. The image shows a "
            "large coil of continuous-cast copper rod (8mm diameter) resting on a wooden pallet, "
            "against a clean white background. The rod is bright copper-colored, coiled into a "
            "large flat pancake shape, secured with metal bands.\n\n"
            "I need this elevated to premium studio product photography. Generate a photorealistic "
            "hero shot of this copper rod coil. Remove or replace the wooden pallet — instead, "
            "place the coil on a clean, low-profile white or warm cream surface that suggests "
            "stability without being distracting. The surface can have a very faint warm reflection.\n\n"
            "Lighting: Dramatic warm studio lighting that makes the copper rod surface GLOW. "
            "Key light from camera left at 45 degrees, creating bright copper-gold highlights "
            "along the upper curves of the rod coil. The copper should appear rich, warm, and "
            "pure — the color of freshly cast bright copper (#CE7340 highlights sweeping into "
            "deep #8B4A28 in shadow). Individual rod passes should be distinguishable — you "
            "should be able to trace the rod winding from outside to center.\n\n"
            "Camera: Slightly elevated 20-degree angle looking down at the coil to reveal the "
            "flat spiral form. 50mm lens at f/8 for the full coil in sharp focus. The coil "
            "should fill 85% of the frame width.\n\n"
            "The overall impression: industrial power and material purity. This is Pakistan's "
            "highest-purity copper rod — the image should radiate that quality.\n\n"
            "No text, no logos, no people. "
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 5 — CCR Copper Rod",
        "option": "A (with reference image)",
    },

    "banner5_copper_rod_optB": {
        "filename": "banner5_copper_rod_optB.png",
        "reference": None,
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Generate a photorealistic premium studio hero photograph of a large "
            "continuous-cast copper rod coil (CCR — Continuous Cast Rod).\n\n"
            "The product: A large flat pancake coil of 8mm diameter bright copper rod. The rod is "
            "coiled in concentric rings from outside to center, the individual passes of rod clearly "
            "visible and distinguishable. The copper rod surface is bright, warm, and highly metallic "
            "— the color of freshly cast, high-purity copper: rich reddish-amber in full light, "
            "deepening to warm dark copper in shadow areas. The rod surface shows very slight surface "
            "sheen — not mirror-polished, but the metallic quality is evident.\n\n"
            "The coil sits on a minimal clean white surface. The coil diameter suggests it weighs "
            "hundreds of kilograms — this is industrial scale. The proportions communicate mass "
            "and substance.\n\n"
            "Lighting: Dramatic warm studio lighting. Strong warm key light from camera left at "
            "45 degrees, creating a sweeping highlight band across the upper arc of the coil — "
            "the copper glows here. Soft fill from camera right at one-third intensity. Very subtle "
            "rim light from above, creating a highlight on the topmost pass of the rod.\n\n"
            "Camera: 20-degree elevated angle looking slightly down on the coil from the front. "
            "The full coil fills 85% of the image width. 50mm lens, f/8, full depth of field.\n\n"
            "Background: Pure white (#FFFFFF) to warm cream (#FAF8F5) gradient. Clean, uncluttered.\n\n"
            "The image must communicate: purity, scale, quality, industrial strength — this is "
            "Pakistan's finest copper rod.\n\n"
            "No text, no logos, no props. "
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 5 — CCR Copper Rod",
        "option": "B (text-only)",
    },

    # ── Banner 6: NMN Nomex Insulation ────────────────────────────────────────
    "banner6_nmn_optA": {
        "filename": "banner6_nmn_optA.png",
        "reference": "insulation-materials/NMN.jpeg",
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Use the uploaded reference image as a scale and format reference (it shows NMN Nomex "
            "insulation material in cylindrical roll form). Do NOT replicate the packaging or grey "
            "background from the reference.\n\n"
            "Generate a photorealistic premium studio product photograph showing a curated "
            "arrangement of NMN (Nomex-Mylar-Nomex) electrical insulation rolls for transformer "
            "manufacturing. Show three rolls of varying heights arranged in a staggered group — "
            "two in front, one slightly behind and taller.\n\n"
            "The rolls should have this appearance:\n"
            "- Off-white / natural cream color (Nomex composite material)\n"
            "- Slightly fibrous, matte surface texture — like high-quality technical non-woven fabric\n"
            "- Clean-cut flat top and bottom edges, no visible packaging\n"
            "- Small circular cardboard core visible at the top center of each roll\n"
            "- The surface shows the precision of industrial manufacturing\n\n"
            "Background and surface: Pure white (#FFFFFF). Soft even overhead studio lighting with "
            "gentle warm accent from camera left. The lighting should reveal the subtle fibrous "
            "surface texture of the Nomex material.\n\n"
            "Camera: Eye-level or very slightly elevated angle. All rolls in sharp focus. "
            "50mm lens at f/8.\n\n"
            "This image communicates: precision, engineered quality, premium insulation materials.\n\n"
            "No text, no logos. "
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 6 — NMN Nomex Insulation",
        "option": "A (with reference image)",
    },

    "banner6_nmn_optB": {
        "filename": "banner6_nmn_optB.png",
        "reference": None,
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Generate a photorealistic premium studio product photograph of NMN (Nomex-Mylar-Nomex) "
            "electrical insulation material rolls for transformer manufacturing.\n\n"
            "Show three cylindrical rolls of varying heights arranged in a staggered composition — "
            "two in the foreground, one taller roll slightly behind in the center. "
            "The rolls have:\n"
            "- Off-white to natural cream color (the NMN composite material)\n"
            "- Subtle fibrous surface texture — the Nomex non-woven fabric layer gives a gentle, "
            "slightly rough matte finish\n"
            "- Clean precision-cut flat edges top and bottom\n"
            "- A small visible cardboard core circle at the top of each roll\n"
            "- No plastic wrapping, no packaging — the finished material surface is visible\n\n"
            "Background: Pure white (#FFFFFF). Studio lighting.\n\n"
            "Lighting: Soft, warm overhead studio light with a gentle accent from camera left. "
            "The light reveals the texture of the Nomex surface without harsh shadows. "
            "Warm-neutral color temperature — not cool or blue.\n\n"
            "The image communicates: engineered precision, layered insulation technology, "
            "premium transformer materials.\n\n"
            "No text, no logos. "
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 6 — NMN Nomex Insulation",
        "option": "B (text-only)",
    },

    # ── Banner 6: DMD Insulation ──────────────────────────────────────────────
    "banner6_dmd_optA": {
        "filename": "banner6_dmd_optA.png",
        "reference": "insulation-materials/DMD_Insulation_Paper.jpg",
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Use the uploaded product photograph as the subject reference. The image shows four "
            "tall cylindrical rolls of insulation material in various colors. Use this for the "
            "product form and arrangement only — do NOT use the pink, green, blue, grey colors "
            "from the reference. Do NOT use the grey background.\n\n"
            "Generate a photorealistic premium studio product photograph of DMD (Dacron-Mylar-Dacron) "
            "electrical insulation material rolls, presented on a clean pure white background.\n\n"
            "Show four tall cylindrical rolls arranged in a clean composition. The rolls should have:\n"
            "- Warm tan / natural beige color (#D4A976 range — similar to kraft paper)\n"
            "- Smooth surface with subtle fiber texture visible — DMD has a slightly different "
            "texture than kraft paper, more uniform\n"
            "- Clean precision-cut flat edges\n"
            "- No labels, no packaging, no plastic wrapping\n\n"
            "Background: Pure white (#FFFFFF) studio background. Clean white surface.\n\n"
            "Lighting: Even, soft overhead studio lighting with gentle warm accent from camera "
            "left — reveals the surface texture. Warm-neutral light.\n\n"
            "Camera: Eye-level or very slightly elevated. All rolls in sharp focus. "
            "50mm lens at f/8.\n\n"
            "This image communicates: precision, layered protection, engineered quality.\n\n"
            "No text, no logos. "
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 6 — DMD Insulation",
        "option": "A (with reference image)",
    },

    "banner6_dmd_optB": {
        "filename": "banner6_dmd_optB.png",
        "reference": None,
        "aspect_ratio": "2:3",
        "prompt": (
            f"{STYLE_PREFIX} "
            "Generate a photorealistic premium studio product photograph of a curated set of "
            "electrical insulation materials for transformer manufacturing. The image should show "
            "an elegant, staggered arrangement of five cylindrical material rolls of varying "
            "heights, presented as precision-engineered industrial components.\n\n"
            "The rolls:\n"
            "- The tallest roll (center-back): Off-white, slightly fibrous Nomex-composite surface "
            "(NMN — Nomex-Mylar-Nomex). Subtle fabric-like texture catching light as gentle micro-detail. "
            "Height approximately 1.5x the diameter.\n"
            "- Two medium rolls (front-left and front-right): Warm natural tan, smooth surface "
            "(DMD — Dacron-Mylar-Dacron insulation paper). Color similar to natural kraft paper "
            "but smoother.\n"
            "- Two shorter rolls (mid-background): One cream-white, one very faint warm amber — "
            "completing the group.\n\n"
            "Each roll has clean-cut flat top and bottom edges, no visible packaging. The cardboard "
            "core is visible as a small circle in the top center of each roll. The surfaces show "
            "the precision of industrial manufacturing.\n\n"
            "In the very foreground, a small flat sheet of insulation material is partially visible "
            "— folded once, showing the clean cross-section of the material layers: translucent "
            "film sandwiched between fibrous non-woven layers.\n\n"
            "Composition: The five rolls form a pyramid arrangement — centered, staggered for depth. "
            "The partial sheet adds a foreground layer. 50mm lens at f/8, all elements in sharp focus.\n\n"
            "Background and surface: Pure white (#FFFFFF). Soft even overhead studio lighting with "
            "warm accent from camera left. Subtle, warm shadow beneath each roll for grounding.\n\n"
            "The image communicates: engineered precision, layered insulation technology, "
            "premium materials.\n\n"
            "No text, no logos. "
            "Photorealistic commercial product photography. 2:3 portrait aspect ratio. 4K resolution."
        ),
        "banner": "Banner 6 — DMD Insulation",
        "option": "B (text-only)",
    },

    # ── Atmospheric: Copper Texture Background ────────────────────────────────
    "atmosphere_copper_texture": {
        "filename": "atmosphere_copper_texture.png",
        "reference": None,
        "aspect_ratio": "1:1",
        "prompt": (
            "Generate a close-up photorealistic photograph of a copper metal surface texture for "
            "use as a large-format background image. The surface shows the natural, organic texture "
            "of drawn copper wire seen from extremely close — the surface is a dense weave or "
            "winding of very fine copper strands, creating a rich, warm textural field. The copper "
            "color ranges from light amber-gold (#F5B880) in the highlights to deeper warm copper "
            "(#CE7340) in the recesses between strands.\n\n"
            "The image should have no single dominant focal point — it is a pure texture field. "
            "The texture should feel luxurious and warm, like looking at the surface of a large "
            "copper enamelled wire spool under studio light.\n\n"
            "Lighting: Very gentle, diffused, even warm studio lighting — soft enough to avoid "
            "harsh shadows but with enough direction to reveal the three-dimensional texture of "
            "each strand. Warm color temperature throughout.\n\n"
            "The final image should work at very low opacity (15-25%) as a background overlay "
            "layer in banner design — so the texture should be subtle enough not to compete with "
            "foreground content.\n\n"
            "No sharp edges, no isolated objects, no text. This is a pure texture image.\n\n"
            "1:1 square aspect ratio (for flexible cropping in design). 4K resolution. Photorealistic."
        ),
        "banner": "Atmospheric — Copper Texture Background",
        "option": "Text-only",
    },

    # ── Atmospheric: Manufacturing Background ─────────────────────────────────
    "atmosphere_manufacturing": {
        "filename": "atmosphere_manufacturing.png",
        "reference": None,
        "aspect_ratio": "9:16",
        "prompt": (
            "Generate a photorealistic atmospheric photograph of a copper wire manufacturing "
            "facility, shot with extreme shallow depth of field so that the entire image is "
            "softly defocused — approximately 80% blurred, like the background of a portrait "
            "photograph.\n\n"
            "What is visible (all very soft and impressionistic): warm orange-copper tones from "
            "copper wire under production lights, the implied circular forms of wire spools, soft "
            "industrial overhead lighting creating warm pools of light, a general warm amber-copper "
            "atmospheric color field.\n\n"
            "The image should feel warm, purposeful, and industrial — but no sharp details, no "
            "readable text, no identifiable faces. Pure warm atmospheric blur.\n\n"
            "Color palette: Dominant warm amber-copper tones (#F5B880, #E8A065) fading into "
            "darker warm background. Some brighter light-source points (very soft, like bokeh "
            "circles of warm light) visible in the background.\n\n"
            "This image works as a full-banner background layer at low opacity (20-30%) to suggest "
            "manufacturing context without competing with product images and text.\n\n"
            "9:16 portrait aspect ratio for full banner bleed. 4K resolution. Photorealistic."
        ),
        "banner": "Atmospheric — Manufacturing Background (Banner 1/2)",
        "option": "Text-only",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# IMAGE GENERATION FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def init_client():
    """Initialize the Gemini API client."""
    if USE_NEW_SDK:
        return genai.Client(api_key=API_KEY)
    else:
        genai_legacy.configure(api_key=API_KEY)
        return None


def load_reference_image(ref_rel_path: str):
    """Load a reference image from disk. Returns PIL Image or None."""
    if not ref_rel_path:
        return None
    full_path = REF_DIR / ref_rel_path
    if not full_path.exists():
        print(f"  [WARN] Reference image not found: {full_path}")
        return None
    try:
        img = Image.open(full_path)
        # Convert RGBA to RGB if needed (JPEG doesn't support alpha)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        print(f"  [REF]  Loaded {full_path.name} ({img.size[0]}x{img.size[1]})")
        return img
    except Exception as e:
        print(f"  [WARN] Could not load reference image: {e}")
        return None


def generate_image_new_sdk(client, model_name: str, prompt_text: str,
                            ref_image, aspect_ratio: str):
    """Generate an image using the new google-genai SDK."""
    from google.genai import types

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
    )

    if ref_image is not None:
        contents = [prompt_text, ref_image]
    else:
        contents = prompt_text

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=config,
    )
    return response


def generate_image_legacy_sdk(model_name: str, prompt_text: str,
                               ref_image, aspect_ratio: str):
    """Generate an image using the legacy google-generativeai SDK."""
    import warnings
    warnings.filterwarnings("ignore")

    model = genai_legacy.GenerativeModel(
        model_name,
        generation_config={"response_modalities": ["TEXT", "IMAGE"]},
    )
    # Note: legacy SDK does not support image_config aspect_ratio natively
    if ref_image is not None:
        response = model.generate_content([prompt_text, ref_image])
    else:
        response = model.generate_content(prompt_text)
    return response


def extract_image_bytes(response) -> bytes:
    """Extract image bytes from a Gemini response (both SDK variants)."""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                return bytes(inline.data)
    return None


def save_image(image_bytes: bytes, output_path: Path, mime_type: str = "image/jpeg"):
    """Save raw image bytes to PNG using PIL."""
    img = Image.open(io.BytesIO(image_bytes))
    img.save(str(output_path), format="PNG")
    return output_path.stat().st_size


def generate_with_retry(client, key: str, config: dict, force: bool = False) -> dict:
    """
    Generate a single image with retries and fallback model support.
    Returns a result dict with status, filename, size, model used, error.
    """
    output_path = OUTPUT_DIR / config["filename"]
    result = {
        "key": key,
        "filename": config["filename"],
        "banner": config["banner"],
        "option": config["option"],
        "aspect_ratio": config["aspect_ratio"],
        "reference": config.get("reference"),
        "status": "pending",
        "model_used": None,
        "file_size_kb": None,
        "error": None,
        "timestamp": None,
    }

    # Skip if already exists and not forcing
    if output_path.exists() and not force:
        size_kb = output_path.stat().st_size // 1024
        print(f"  [SKIP] Already exists: {config['filename']} ({size_kb} KB)")
        result["status"] = "skipped"
        result["file_size_kb"] = size_kb
        return result

    ref_image = load_reference_image(config.get("reference"))
    prompt_text = config["prompt"]
    aspect_ratio = config["aspect_ratio"]

    models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]

    for model_name in models_to_try:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"  [GEN]  Attempt {attempt}/{MAX_RETRIES} using {model_name} ...")

                if USE_NEW_SDK:
                    response = generate_image_new_sdk(
                        client, model_name, prompt_text, ref_image, aspect_ratio
                    )
                else:
                    response = generate_image_legacy_sdk(
                        model_name, prompt_text, ref_image, aspect_ratio
                    )

                image_bytes = extract_image_bytes(response)
                if not image_bytes:
                    raise ValueError("Response contained no image data")

                size_bytes = save_image(image_bytes, output_path)
                size_kb = size_bytes // 1024
                print(f"  [OK]   Saved {config['filename']} — {size_kb} KB")
                result.update({
                    "status": "success",
                    "model_used": model_name,
                    "file_size_kb": size_kb,
                    "timestamp": datetime.now().isoformat(),
                })
                return result

            except Exception as e:
                error_str = str(e)
                print(f"  [ERR]  {error_str[:120]}")

                # Rate limit — wait and retry
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    wait = RETRY_WAIT * attempt
                    print(f"  [WAIT] Rate limited. Waiting {wait}s before retry...")
                    time.sleep(wait)
                    continue

                # Model not available — try next model
                if "404" in error_str or "not found" in error_str.lower() or "does not exist" in error_str.lower():
                    print(f"  [SKIP] Model {model_name} not available, trying next...")
                    break

                # Other error on last attempt — record and continue
                if attempt == MAX_RETRIES:
                    result.update({
                        "status": "failed",
                        "error": error_str[:300],
                        "model_used": model_name,
                        "timestamp": datetime.now().isoformat(),
                    })

    if result["status"] == "pending":
        result.update({
            "status": "failed",
            "error": "All models and retries exhausted",
            "timestamp": datetime.now().isoformat(),
        })

    return result


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generate trade show banner images via Gemini API")
    parser.add_argument("--force", action="store_true", help="Regenerate all images, overwriting existing")
    args = parser.parse_args()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("  CWIEME Berlin 2026 — Image Generation Script")
    print("  Universal Metals Pakistan Limited")
    print(f"  Model: {PRIMARY_MODEL} (Nano Banana Pro)")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Force regenerate: {args.force}")
    print("=" * 65)

    client = init_client()
    results = []
    total = len(PROMPTS)

    for i, (key, config) in enumerate(PROMPTS.items(), 1):
        print(f"\n[{i}/{total}] {config['banner']} — Option {config['option']}")
        print(f"         File: {config['filename']}")
        if config.get("reference"):
            print(f"         Ref:  {config['reference']}")

        result = generate_with_retry(client, key, config, force=args.force)
        results.append(result)

        # Delay between requests (except after last item or skipped items)
        if i < total and result["status"] not in ("skipped",):
            print(f"  [WAIT] Pausing {DELAY_BETWEEN_REQUESTS}s to respect rate limits...")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  GENERATION SUMMARY")
    print("=" * 65)

    success  = [r for r in results if r["status"] == "success"]
    skipped  = [r for r in results if r["status"] == "skipped"]
    failed   = [r for r in results if r["status"] == "failed"]

    print(f"  Successful: {len(success)}")
    print(f"  Skipped (existing): {len(skipped)}")
    print(f"  Failed: {len(failed)}")

    if success:
        print("\n  Successfully generated:")
        for r in success:
            print(f"    {r['filename']:45s} {r['file_size_kb']:>6} KB  [{r['model_used']}]")

    if skipped:
        print("\n  Skipped (already exist — use --force to regenerate):")
        for r in skipped:
            size = r["file_size_kb"] or "?"
            print(f"    {r['filename']:45s} {str(size):>6} KB")

    if failed:
        print("\n  Failed:")
        for r in failed:
            print(f"    {r['filename']}")
            if r.get("error"):
                print(f"      Error: {r['error'][:100]}")

    # ── Save log ──────────────────────────────────────────────────────────────
    log_data = {
        "generated_at": datetime.now().isoformat(),
        "model_primary": PRIMARY_MODEL,
        "model_fallback": FALLBACK_MODEL,
        "total": total,
        "success": len(success),
        "skipped": len(skipped),
        "failed": len(failed),
        "results": results,
    }
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2)
    print(f"\n  Log saved: {LOG_FILE}")
    print("=" * 65)

    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
