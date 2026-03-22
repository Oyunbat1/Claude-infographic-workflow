#!/usr/bin/env python3
"""
Generate an infographic using Replicate's Nano Banana Pro API.

Usage:
    python3 generate_infographic.py --prompt "..." --output output/infographic.png --aspect-ratio 9:16

Requires:
    pip install replicate
    export REPLICATE_API_TOKEN='your-token-here'
"""

import os
import sys
import time
import threading
import argparse
from datetime import datetime

try:
    import replicate
except ImportError:
    print("ERROR: replicate package not installed. Run: pip install replicate --break-system-packages", file=sys.stderr)
    sys.exit(1)


def spinner(stop_event, message="Үүсгэж байна"):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    start = time.time()
    while not stop_event.is_set():
        elapsed = int(time.time() - start)
        sys.stderr.write(f"\r  {frames[i % len(frames)]}  {message}... {elapsed}s ")
        sys.stderr.flush()
        time.sleep(0.1)
        i += 1
    sys.stderr.write("\r" + " " * 50 + "\r")
    sys.stderr.flush()


def main():
    parser = argparse.ArgumentParser(description="Generate infographic via Nano Banana Pro")
    parser.add_argument("--prompt", required=True, help="Generation prompt")
    parser.add_argument("--output", default="output/infographic.png", help="Output PNG path")
    parser.add_argument("--aspect-ratio", default="9:16",
                        choices=["9:16", "3:4", "1:1", "16:9", "4:3", "4:5", "5:4"])
    args = parser.parse_args()

    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print("ERROR: REPLICATE_API_TOKEN тохируулаагүй байна.", file=sys.stderr)
        print("Set it with: export REPLICATE_API_TOKEN='your-token-here'", file=sys.stderr)
        sys.exit(1)

    print(f"\n🎨 Инфографик үүсгэж байна...", file=sys.stderr)
    print(f"   Харьцаа : {args.aspect_ratio}", file=sys.stderr)

    # Quality-boosted prompt suffi
    enhanced_prompt = (
        args.prompt +
        " High quality, sharp text, high resolution, detailed, professional print quality."
    )

    stop_event = threading.Event()
    spin_thread = threading.Thread(target=spinner, args=(stop_event, "Replicate API дуудаж байна"))
    spin_thread.start()

    try:
        prediction = replicate.predictions.create(
            model="google/nano-banana-pro",
            input={
                "prompt": enhanced_prompt,
                "aspect_ratio": args.aspect_ratio,
                "output_format": "png",
                "output_quality": 100,
            }
        )

        # Poll until done
        while prediction.status not in ("succeeded", "failed", "canceled"):
            time.sleep(1)
            prediction.reload()

        stop_event.set()
        spin_thread.join()

        if prediction.status != "succeeded":
            print(f"\nERROR: Генерац амжилтгүй болсон — {prediction.error}", file=sys.stderr)
            sys.exit(1)

        output = prediction.output
        # output may be a list or a single URL
        if isinstance(output, list):
            output = output[0]

        # Download the image — add timestamp to preserve previous images
        import urllib.request
        base, ext = os.path.splitext(args.output)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{base}_{timestamp}{ext}"
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        urllib.request.urlretrieve(str(output), output_path)

        file_size = os.path.getsize(output_path)
        print(f"✅ Хадгалагдлаа: {output_path} ({file_size / 1024:.1f} KB)", file=sys.stderr)
        print(output_path)

    except Exception as e:
        stop_event.set()
        spin_thread.join()
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
