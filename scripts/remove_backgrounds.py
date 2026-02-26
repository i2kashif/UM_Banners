#!/usr/bin/env python3
"""
remove_backgrounds.py
Remove backgrounds from product images, making them fully transparent (alpha=0).
Uses BFS flood-fill from image borders + edge feathering via scipy distance transform.
"""

from PIL import Image, ImageFilter
import numpy as np
from collections import deque
from scipy.ndimage import distance_transform_edt
import os


def remove_background(input_path, output_path, threshold=35, edge_softness=3):
    """
    Remove background using flood-fill from edges, setting background to transparent.

    Args:
        input_path:    Path to source image.
        output_path:   Path to save PNG with transparency.
        threshold:     Max per-channel difference from sampled bg color to consider a pixel background.
        edge_softness: Distance in pixels for the alpha feather gradient at object edges.
    """
    print(f"  Processing: {os.path.basename(input_path)}")
    img = Image.open(input_path).convert('RGBA')
    data = np.array(img)
    h, w = data.shape[:2]

    # Sample background color from image borders (top/bottom rows, left/right columns)
    border_pixels = np.concatenate([
        data[0, :, :3],           # top row
        data[-1, :, :3],          # bottom row
        data[:, 0, :3],           # left column
        data[:, -1, :3],          # right column
    ])
    bg_color = np.median(border_pixels, axis=0).astype(np.uint8)
    print(f"    Sampled background color: RGB{tuple(bg_color)}")

    # Create visited mask and background mask
    visited = np.zeros((h, w), dtype=bool)
    bg_mask = np.zeros((h, w), dtype=bool)

    # BFS flood fill from all border pixels
    queue = deque()

    # Add all border pixels to queue
    for x in range(w):
        queue.append((0, x))      # top row
        queue.append((h-1, x))    # bottom row
    for y in range(h):
        queue.append((y, 0))      # left column
        queue.append((y, w-1))    # right column

    while queue:
        y, x = queue.popleft()
        if y < 0 or y >= h or x < 0 or x >= w:
            continue
        if visited[y, x]:
            continue
        visited[y, x] = True

        # Check if this pixel is close to background color
        pixel = data[y, x, :3].astype(int)
        diff = np.abs(pixel - bg_color.astype(int))
        if np.max(diff) < threshold:
            bg_mask[y, x] = True
            # Add neighbors (4-connected for speed)
            queue.append((y-1, x))
            queue.append((y+1, x))
            queue.append((y, x-1))
            queue.append((y, x+1))

    bg_pixels = np.count_nonzero(bg_mask)
    total_pixels = h * w
    print(f"    Background pixels found: {bg_pixels} / {total_pixels} ({100*bg_pixels/total_pixels:.1f}%)")

    # Calculate distance from background for non-background pixels
    dist_from_bg = distance_transform_edt(~bg_mask)

    # Create alpha channel: 0 for background, 255 for product, gradient at edges
    alpha = np.ones((h, w), dtype=np.float64) * 255
    alpha[bg_mask] = 0

    # Feather the edges (pixels within edge_softness distance of the boundary)
    if edge_softness > 0:
        edge_zone = (dist_from_bg > 0) & (dist_from_bg <= edge_softness)
        alpha[edge_zone] = (dist_from_bg[edge_zone] / edge_softness) * 255

    # Apply alpha
    data[:, :, 3] = alpha.astype(np.uint8)

    # Set fully transparent pixels to white RGB (prevents dark fringe on any partial blending)
    fully_transparent = alpha == 0
    data[fully_transparent, 0] = 255
    data[fully_transparent, 1] = 255
    data[fully_transparent, 2] = 255

    result = Image.fromarray(data)
    result.save(output_path, 'PNG')
    print(f"    Saved: {output_path} ({result.size[0]}x{result.size[1]})")

    # Verify corner pixels have alpha=0
    result_arr = np.array(result)
    corners = [
        result_arr[0, 0, 3],
        result_arr[0, -1, 3],
        result_arr[-1, 0, 3],
        result_arr[-1, -1, 3],
    ]
    print(f"    Corner alphas (should all be 0): {corners}")
    return result


def main():
    products_dir = "/Users/ibrahimkashif/Desktop/CWEIME/UM_Banners/assets/images/products"

    images = [
        # (input_filename, output_filename, threshold)
        # AI-generated images — light/white backgrounds
        ("copper-enamelled-wire-ai.png",   "copper-enamelled-wire-ai-transparent.png",   35),
        ("paper-covered-strip-ai.png",     "paper-covered-strip-ai-transparent.png",     35),
        ("ccr-copper-rod-ai.png",          "ccr-copper-rod-ai-transparent.png",           35),
        # Original photographs — potentially varied backgrounds
        ("nmn-nomex.jpeg",                 "nmn-nomex-transparent.png",                  50),
        ("dmd-insulation.jpg",             "dmd-insulation-transparent.png",              50),
        ("ama.jpeg",                       "ama-transparent.png",                         50),
        ("film-composite.jpeg",            "film-composite-transparent.png",              50),
        ("pet-film.jpeg",                  "pet-film-transparent.png",                    50),
    ]

    print("=== Background Removal — UMPL Trade Show Banners ===\n")
    for input_name, output_name, threshold in images:
        input_path  = os.path.join(products_dir, input_name)
        output_path = os.path.join(products_dir, output_name)
        if not os.path.exists(input_path):
            print(f"  SKIPPED (not found): {input_path}")
            continue
        remove_background(input_path, output_path, threshold=threshold, edge_softness=3)
        print()

    print("=== All done. ===")


if __name__ == "__main__":
    main()
