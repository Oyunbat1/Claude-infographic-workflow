#!/usr/bin/env python3
"""
Interactive infographic generator.
Asks for a topic, offers content options, aspect ratio, then generates and overlays logo.

Usage:
    python3 run.py                         # interactive mode
    python3 run.py --prompt "..."          # skip topic prompt
    python3 run.py --output out.png
"""

import os
import sys
import json
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BRAND_FOLDER = os.path.join(SCRIPT_DIR, "brand")
EXTRACT_SCRIPT = os.path.join(SCRIPT_DIR, "extract_brand.py")
GENERATE_SCRIPT = os.path.join(SCRIPT_DIR, "generate_infographic.py")

ASPECT_RATIOS = [
    ("9:16", "Босоо — Инстаграм Story, постер (өгөгдмөл)"),
    ("3:4",  "Босоо — Нийтлэл, A4 хэлбэр"),
    ("1:1",  "Квадрат — Нийгмийн сүлжээ"),
    ("16:9", "Хэвтээ — Вэб баннер, слайд"),
    ("4:5",  "Босоо — Инстаграм нийтлэл"),
]


def extract_brand():
    result = subprocess.run(
        [sys.executable, EXTRACT_SCRIPT, BRAND_FOLDER],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR extracting brand: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def build_options(topic):
    return [
        {
            "title": f"{topic} — Статистик",
            "layout": "Статистик",
            "description": "Тооны мэдээлэл, статистик, дүрс бүхий инфографик.",
            "prompt": f"Create a professional vertical infographic poster about '{topic}' in Mongolian Cyrillic. Layout: Statistics style with large numbers, icons, and data points. All text must be in Mongolian Cyrillic script. Title at top, 4-5 key statistics in the middle, brief descriptions under each number.",
        },
        {
            "title": f"{topic} — Үе шат",
            "layout": "Үе шат — Алхам алхмаар",
            "description": "Дугаарласан алхмуудаар дээрээс доош урсах гарын авлага.",
            "prompt": f"Create a professional vertical infographic poster about '{topic}' in Mongolian Cyrillic. Layout: Step-by-step process with numbered steps (1-5), connected by arrows flowing top to bottom. All text must be in Mongolian Cyrillic script. Bold title at top, each step has a short heading and one-line description.",
        },
        {
            "title": f"{topic} — Цагийн хуваарь",
            "layout": "Цагийн хуваарь — Он цаг",
            "description": "Түүх эсвэл хөгжлийг он цагийн дарааллаар харуулсан загвар.",
            "prompt": f"Create a professional vertical infographic poster about '{topic}' in Mongolian Cyrillic. Layout: Vertical timeline with milestones/events listed chronologically. All text must be in Mongolian Cyrillic script. Title at top, timeline line in center, dates/labels on alternating sides.",
        },
        {
            "title": f"{topic} — Жагсаалт",
            "layout": "Жагсаалт — Чухал баримтууд",
            "description": "Хамгийн чухал баримт эсвэл зөвлөмжүүдийн тод жагсаалт.",
            "prompt": f"Create a professional vertical infographic poster about '{topic}' in Mongolian Cyrillic. Layout: Top 5 facts or tips list with bold numbered items and checkmark icons. All text must be in Mongolian Cyrillic script. Eye-catching title at top, each fact in its own card/row with a short headline and brief detail.",
        },
    ]


def inject_brand(prompt, brand):
    palette = brand.get("suggested_palette", {})
    primary = palette.get("primary", "#1a365d")
    secondary = palette.get("secondary", "#2b6cb0")
    accent = palette.get("accent", "#ed8936")

    return f"""{prompt}

BRAND COLORS:
- Primary: {primary} (headers, main elements)
- Secondary: {secondary} (backgrounds, cards)
- Accent: {accent} (highlights, call-outs)

STYLE: Clean, modern, professional, corporate
TYPOGRAPHY: Bold headers, clear body text, all Mongolian Cyrillic
BACKGROUND: Gradient or solid using brand colors
Important: Every piece of text must be in Mongolian Cyrillic script."""


def overlay_logo(image_path, logo_path):
    """Overlay brand logo onto the generated infographic (bottom-right corner)."""
    try:
        from PIL import Image
    except ImportError:
        print("  ⚠️  Pillow суулгаагүй байна — лого нэмэхгүй. (pip install Pillow)", file=sys.stderr)
        return

    try:
        base = Image.open(image_path).convert("RGBA")
        logo = Image.open(logo_path).convert("RGBA")

        # Resize logo to ~25% of infographic width
        logo_w = int(base.width * 0.25)
        ratio = logo_w / logo.width
        logo_h = int(logo.height * ratio)
        logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

        # Position: bottom-right with 20px padding
        padding = 20
        x = base.width - logo_w - padding
        y = base.height - logo_h - padding

        # Paste with alpha mask
        base.paste(logo, (x, y), logo)
        base.convert("RGB").save(image_path)
        print(f"  🏷️  Лого нэмэгдлээ ({logo_w}x{logo_h}px, баруун доод буланд)", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️  Лого нэмэхэд алдаа гарлаа: {e}", file=sys.stderr)


def ask_topic():
    print("\n" + "="*52)
    print("    Монгол Инфографик Үүсгэгч")
    print("="*52)
    topic = input("\nТемаа оруулна уу: ").strip()
    if not topic:
        print("Тема оруулаагүй байна. Гарч байна.")
        sys.exit(0)
    return topic


def ask_option(options):
    print("\nИнфографикийн сонголтууд:\n")
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt['title']}")
        print(f"      Загвар   : {opt['layout']}")
        print(f"      Тайлбар  : {opt['description']}")
        print()
    while True:
        choice = input(f"Сонголт хийнэ үү (1-{len(options)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(f"1-ээс {len(options)} хүртэлх тоо оруулна уу.")


def ask_aspect_ratio():
    print("\nХэмжээний харьцаа сонгоно уу:\n")
    for i, (ratio, desc) in enumerate(ASPECT_RATIOS, 1):
        print(f"  [{i}] {ratio:5s}  —  {desc}")
    print()
    while True:
        choice = input(f"Сонголт хийнэ үү (1-{len(ASPECT_RATIOS)}) [өгөгдмөл: 1]: ").strip()
        if choice == "":
            return ASPECT_RATIOS[0][0]
        if choice.isdigit() and 1 <= int(choice) <= len(ASPECT_RATIOS):
            return ASPECT_RATIOS[int(choice) - 1][0]
        print(f"1-ээс {len(ASPECT_RATIOS)} хүртэлх тоо оруулна уу.")


def main():
    parser = argparse.ArgumentParser(description="Interactive Mongolian infographic generator")
    parser.add_argument("--prompt", help="Skip interactive mode and use this prompt directly")
    parser.add_argument("--output", default="output/infographic.png", help="Output PNG path")
    parser.add_argument("--aspect-ratio", choices=["9:16", "3:4", "1:1", "16:9", "4:3", "4:5", "5:4"],
                        help="Skip aspect ratio selection")
    parser.add_argument("--no-brand", action="store_true", help="Skip brand extraction")
    args = parser.parse_args()

    # Step 1: Extract brand
    brand = {}
    logo_path = None
    if not args.no_brand:
        print("\n📂 Брэндийн файлуудыг уншиж байна...")
        brand = extract_brand()
        logo_path = brand.get("logo")
        palette = brand.get("suggested_palette", {})
        print(f"   Лого    → {logo_path or 'олдсонгүй'}")
        print(f"   Өнгөнүүд → {palette}")

    # Step 2: Get prompt — interactive or direct
    if args.prompt:
        final_prompt = args.prompt
        aspect_ratio = args.aspect_ratio or "9:16"
    else:
        topic = ask_topic()
        options = build_options(topic)
        chosen = ask_option(options)
        final_prompt = chosen["prompt"]
        print(f"\n✅ Сонгосон: {chosen['title']}")

        # Step 3: Ask aspect ratio
        aspect_ratio = args.aspect_ratio or ask_aspect_ratio()
        print(f"✅ Харьцаа  : {aspect_ratio}")

    # Step 4: Inject brand colors into prompt
    if brand:
        final_prompt = inject_brand(final_prompt, brand)

    # Step 5: Generate
    print("\n🎨 Инфографик үүсгэж байна...")
    result = subprocess.run(
        [sys.executable, GENERATE_SCRIPT,
         "--prompt", final_prompt,
         "--output", args.output,
         "--aspect-ratio", aspect_ratio],
        capture_output=False
    )

    if result.returncode != 0:
        sys.exit(result.returncode)

    # Step 6: Overlay logo
    if logo_path and os.path.exists(logo_path):
        overlay_logo(args.output, logo_path)

    print(f"\n🖼️  Дууслаа! Файл: {args.output}")


if __name__ == "__main__":
    main()
