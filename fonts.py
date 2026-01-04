#!/usr/bin/env python3

import argparse
import re
from pathlib import Path

from libs.convert_font_to_butano import convert_font

DEBUG = False


def debug_print(*args):
    if DEBUG:
        print(*args)


def find_font_directories(font_path):
    font_dirs = []
    base_path = Path(font_path)

    if not base_path.exists():
        raise ValueError(f"Font path does not exist: {font_path}")

    for item in base_path.iterdir():
        if item.is_dir():
            has_txt = any(item.glob("*.txt"))
            has_png = any(item.glob("*.png"))
            if has_txt and has_png:
                font_dirs.append(item)

    return sorted(font_dirs, key=lambda x: x.name)


def main():
    global DEBUG

    parser = argparse.ArgumentParser(description="Convert font assets to Butano format")
    parser.add_argument(
        "font_path", type=str, help="Path to the directory containing font directories"
    )
    parser.add_argument(
        "graphics_dir", type=str, help="Output directory for BMP and JSON files"
    )
    parser.add_argument(
        "includes_dir", type=str, help="Output directory for C++ header files"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()
    DEBUG = args.debug

    font_dirs = find_font_directories(args.font_path)

    debug_print(f"Found {len(font_dirs)} font directories to convert\n")
    debug_print("=" * 70)

    successful = []
    failed = []

    for i, font_dir in enumerate(font_dirs, 1):
        font_name = font_dir.name
        if "_v" in font_name:
            font_name = font_name.rsplit("_v", 1)[0]
        font_name = re.sub(r"_\d+$", "", font_name)

        debug_print(f"\n[{i}/{len(font_dirs)}] {font_dir.name}")
        debug_print("-" * 70)

        try:
            _result = convert_font(
                str(font_dir), args.graphics_dir, args.includes_dir, font_name
            )
            successful.append(font_name)
        except Exception as e:
            debug_print(f"  ✗ ERROR: {e}")
            failed.append((font_name, str(e)))

    debug_print("\n" + "=" * 70)
    debug_print("CONVERSION SUMMARY")
    debug_print("=" * 70)
    debug_print(f"✓ Successful: {len(successful)}/{len(font_dirs)}")
    debug_print(f"✗ Failed: {len(failed)}/{len(font_dirs)}")

    if successful:
        debug_print("\nSuccessfully converted fonts:")
        for name in successful:
            debug_print(f"  - {name}")

    if failed:
        debug_print("\nFailed conversions:")
        for name, error in failed:
            debug_print(f"  - {name}: {error}")

    debug_print("\n✓ Batch conversion complete!")


if __name__ == "__main__":
    main()
