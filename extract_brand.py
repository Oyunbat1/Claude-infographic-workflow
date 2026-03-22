#!/usr/bin/env python3
"""
Extract brand assets from a brand folder.
Finds logo, template, and extracts dominant colors.
Outputs a JSON summary.
"""

import os
import sys
import json
import struct
import zlib
from pathlib import Path


def find_files_by_type(folder, extensions):
    """Find files matching given extensions in folder."""
    results = []
    for f in Path(folder).rglob("*"):
        if f.suffix.lower() in extensions:
            results.append(str(f))
    return results


def read_png_colors(png_path):
    """Extract dominant colors from a PNG by sampling pixels. Minimal implementation."""
    try:
        with open(png_path, "rb") as f:
            signature = f.read(8)
            if signature != b'\x89PNG\r\n\x1a\n':
                return []

            chunks = {}
            while True:
                length_bytes = f.read(4)
                if len(length_bytes) < 4:
                    break
                length = struct.unpack(">I", length_bytes)[0]
                chunk_type = f.read(4).decode("ascii", errors="ignore")
                data = f.read(length)
                f.read(4)  # CRC

                if chunk_type == "IHDR":
                    width = struct.unpack(">I", data[0:4])[0]
                    height = struct.unpack(">I", data[4:8])[0]
                    bit_depth = data[8]
                    color_type = data[9]
                    chunks["IHDR"] = {
                        "width": width, "height": height,
                        "bit_depth": bit_depth, "color_type": color_type
                    }
                elif chunk_type == "IDAT":
                    if "IDAT" not in chunks:
                        chunks["IDAT"] = b""
                    chunks["IDAT"] += data
                elif chunk_type == "IEND":
                    break

            if "IHDR" not in chunks or "IDAT" not in chunks:
                return []

            ihdr = chunks["IHDR"]
            if ihdr["color_type"] not in (2, 6):  # RGB or RGBA only
                return []

            raw = zlib.decompress(chunks["IDAT"])
            w, h = ihdr["width"], ihdr["height"]
            channels = 3 if ihdr["color_type"] == 2 else 4
            stride = 1 + w * channels

            color_counts = {}
            step = max(1, h // 20)
            for y in range(0, h, step):
                row_start = y * stride + 1
                for x in range(0, w, max(1, w // 20)):
                    px_start = row_start + x * channels
                    if px_start + 3 <= len(raw):
                        r, g, b = raw[px_start], raw[px_start+1], raw[px_start+2]
                        # Quantize to reduce noise
                        r = (r // 32) * 32
                        g = (g // 32) * 32
                        b = (b // 32) * 32
                        # Skip near-white and near-black
                        if (r + g + b) < 64 or (r + g + b) > 700:
                            continue
                        key = (r, g, b)
                        color_counts[key] = color_counts.get(key, 0) + 1

            sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])
            top_colors = []
            for (r, g, b), count in sorted_colors[:6]:
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                top_colors.append(hex_color)
            return top_colors

    except Exception as e:
        return []


def parse_color_config(folder):
    """Try to find color definitions in config files."""
    colors = {}
    config_extensions = {".json", ".yaml", ".yml", ".css", ".txt", ".toml", ".ini", ".conf"}

    for f in Path(folder).rglob("*"):
        if f.suffix.lower() in config_extensions:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")

                # Try JSON
                if f.suffix.lower() == ".json":
                    try:
                        data = json.loads(content)
                        if isinstance(data, dict):
                            for key, val in data.items():
                                if isinstance(val, str) and (val.startswith("#") or val.startswith("rgb")):
                                    colors[key] = val
                                elif isinstance(val, dict):
                                    for k2, v2 in val.items():
                                        if isinstance(v2, str) and (v2.startswith("#") or v2.startswith("rgb")):
                                            colors[f"{key}.{k2}"] = v2
                    except json.JSONDecodeError:
                        pass

                # Search for hex color patterns
                import re
                hex_matches = re.findall(r'["\']?(#[0-9a-fA-F]{6})["\']?', content)
                for i, hx in enumerate(hex_matches):
                    if f"hex_{i}" not in colors:
                        colors[f"found_color_{i}"] = hx

            except Exception:
                pass

    return colors


def classify_images(image_files):
    """Classify images as logo or template based on naming."""
    logo = None
    template = None
    others = []

    for f in image_files:
        name = Path(f).stem.lower()
        if any(kw in name for kw in ["logo", "лого", "brand_mark", "icon", "brandmark"]):
            logo = f
        elif any(kw in name for kw in ["template", "загвар", "layout", "background", "bg", "frame"]):
            template = f
        else:
            others.append(f)

    # If not found by name, use heuristics (first smaller image = logo, larger = template)
    if not logo and others:
        logo = others.pop(0)
    if not template and others:
        template = others.pop(0)

    return logo, template, others


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: extract_brand.py <brand_folder_path>"}))
        sys.exit(1)

    folder = sys.argv[1]

    if not os.path.isdir(folder):
        print(json.dumps({"error": f"Brand folder not found: {folder}"}))
        sys.exit(1)

    # Find images
    image_exts = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif"}
    image_files = find_files_by_type(folder, image_exts)

    # Classify
    logo, template, other_images = classify_images(image_files)

    # Extract colors from config files
    config_colors = parse_color_config(folder)

    # Extract colors from logo/template images
    image_colors = []
    for img in [logo, template] + other_images:
        if img and img.lower().endswith(".png"):
            extracted = read_png_colors(img)
            image_colors.extend(extracted)

    # Deduplicate
    seen = set()
    unique_colors = []
    for c in image_colors:
        if c not in seen:
            seen.add(c)
            unique_colors.append(c)

    # Build result
    result = {
        "brand_folder": folder,
        "logo": logo,
        "template": template,
        "other_images": other_images,
        "config_colors": config_colors,
        "extracted_colors": unique_colors[:8],
        "all_files": [str(f) for f in Path(folder).rglob("*") if f.is_file()]
    }

    # Suggest primary/secondary/accent
    all_colors = list(config_colors.values()) + unique_colors
    if len(all_colors) >= 3:
        result["suggested_palette"] = {
            "primary": all_colors[0],
            "secondary": all_colors[1],
            "accent": all_colors[2]
        }
    elif len(all_colors) >= 1:
        result["suggested_palette"] = {
            "primary": all_colors[0],
            "secondary": all_colors[1] if len(all_colors) > 1 else all_colors[0],
            "accent": all_colors[2] if len(all_colors) > 2 else all_colors[0]
        }
    else:
        result["suggested_palette"] = {
            "primary": "#1a365d",
            "secondary": "#2b6cb0",
            "accent": "#ed8936",
            "note": "No colors found in brand folder, using defaults"
        }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
