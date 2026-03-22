---
name: mongolian-infographic
description: Generate infographics with Mongolian Cyrillic text using Replicate's Nano Banana Pro API. Use this skill whenever the user wants to create an infographic, visual data summary, or information poster in Mongolian (Монгол). Triggers include any mention of 'инфографик', 'infographic', 'мэдээллийн зураг', or requests for visual content in Mongolian Cyrillic. Also triggers when the user mentions brand folder, brand colors, logo integration for infographic generation, or asks to generate visual content via Replicate or Nano Banana Pro. Even if the user just says "make me an infographic about X" — use this skill. This skill reads the brand folder at /INFOGRAPIC-AUTOMATION/brand to extract logo, template, and brand colors, then generates content options in Mongolian Cyrillic for the user to pick from, and finally calls the Replicate API to produce a full infographic PNG.
---

# Mongolian Infographic Generator

Generate professional infographics in **Mongolian Cyrillic** using Nano Banana Pro via Replicate. Brand assets come from a fixed folder, content options are proposed to the user, and the final infographic is generated as PNG.

## Prerequisites

Before starting, ensure:
1. `replicate` Python package is installed: `pip install replicate --break-system-packages`
2. `REPLICATE_API_TOKEN` env var is set (user provides this)
3. Brand folder exists at `/INFOGRAPIC-AUTOMATION/brand`

If `REPLICATE_API_TOKEN` is not set, ask the user to provide their token.

## Workflow — 3 Steps

### Step 1: Read Brand Assets

Read the brand folder to find the logo, template, and extract brand colors.

```bash
python3 <skill_path>/scripts/extract_brand.py /INFOGRAPIC-AUTOMATION/brand
```

This outputs JSON with:
- `logo` — path to the logo file
- `template` — path to template/layout reference
- `config_colors` — colors found in config files
- `extracted_colors` — colors extracted from images
- `suggested_palette` — primary, secondary, accent colors

Also visually inspect the logo and template images using the `view` tool to understand the brand's visual identity.

If the brand folder is missing, warn the user and ask them to check the path.

### Step 2: Generate Content Options (Mongolian Cyrillic)

Based on the user's **topic**, generate **4-6 infographic content options** entirely in Mongolian Cyrillic.

Each option must include:
- **Гарчиг (Title)** — catchy, concise Mongolian headline
- **Гол мэдээлэл (Key info)** — 3-6 data points, facts, or steps (short text suitable for infographic)
- **Загварын төрөл (Layout type)** — e.g., Цагийн хуваарь (timeline), Харьцуулалт (comparison), Статистик (statistics), Үе шат (process), Жагсаалт (list)
- **Тайлбар (Description)** — brief description of the visual approach

**Content rules:**
- ALL text MUST be Mongolian Cyrillic (no Latin transliteration)
- Keep text blocks short — infographics need brevity
- Use real, accurate data when possible (search the web if needed)
- Numbers formatted for Mongolian conventions

Present options using `ask_user_input` tool for the user to pick.

### Step 3: Generate Infographic via Replicate

Once the user picks an option, craft a detailed Nano Banana Pro prompt and run:

```bash
REPLICATE_API_TOKEN="$REPLICATE_API_TOKEN" python3 <skill_path>/scripts/generate_infographic.py \
  --prompt "YOUR_DETAILED_PROMPT_HERE" \
  --output output/infographic.png \
  --aspect-ratio "9:16"
```

The script uses the official Replicate Python SDK:
```python
import replicate
output = replicate.run(
    "google/nano-banana-pro",
    input={
        "prompt": prompt,
        "aspect_ratio": "9:16",
        "output_format": "png"
    }
)
with open("output.png", "wb") as f:
    f.write(output.read())
```

#### How to Craft the Prompt

Nano Banana Pro is excellent at rendering multilingual text in images. Structure the prompt like this:

```
Create a professional vertical infographic poster. All text must be in Mongolian Cyrillic script.

TITLE (large, bold, top of poster): "Монгол гарчиг энд"

SECTIONS:
1. "[Монгол текст]" — with [icon description, e.g. bar chart icon]
2. "[Монгол текст]" — with [visual element description]
3. "[Монгол текст]" — with [visual element description]
...

BRAND COLORS:
- Primary: #XXXXXX (use for headers, main elements)
- Secondary: #XXXXXX (use for backgrounds, cards)
- Accent: #XXXXXX (use for highlights, call-outs)

LOGO: Place the brand logo [describe: top-left corner / top-center / bottom]

LAYOUT: Vertical infographic, flowing top to bottom
STYLE: Clean, modern, professional, corporate
TYPOGRAPHY: Bold headers, clear body text, all Mongolian Cyrillic
BACKGROUND: [describe — gradient, solid, pattern based on brand]

Important: Every single piece of text in this infographic must be written in Mongolian Cyrillic script. Make text legible and well-spaced.
```

**Prompt tips for better Mongolian text results:**
- Be extremely explicit about Mongolian Cyrillic — repeat the instruction
- Include the actual Mongolian text in quotes within the prompt
- Describe visual hierarchy clearly (what's big, what's small)
- Reference brand colors by hex code
- Keep fewer text sections for cleaner rendering

#### Aspect Ratios
- `9:16` — Vertical (default, best for infographics & stories)
- `3:4` — Slightly wider vertical
- `1:1` — Square
- `16:9` — Horizontal/landscape

#### If Text Rendering is Poor
If Mongolian Cyrillic results have issues:
1. Simplify — fewer words, larger font areas
2. Make the Cyrillic instruction even more prominent in the prompt
3. Regenerate (results vary per run)
4. Reduce the number of text sections

### Output

Save to `output/infographic.png` and present with `present_files`.

If the user wants adjustments, modify the prompt and regenerate. Common adjustments:
- Color tweaks
- Text corrections
- Layout changes
- Adding/removing sections

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/extract_brand.py` | Analyzes brand folder → JSON with colors, logo, template |
| `scripts/generate_infographic.py` | Calls Replicate SDK → saves PNG |
