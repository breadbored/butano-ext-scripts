#!/usr/bin/env python3

import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image

ORIGINAL_UTF8_CHARS = (
    "Á",
    "É",
    "Í",
    "Ó",
    "Ú",
    "Ü",
    "Ñ",
    "á",
    "é",
    "í",
    "ó",
    "ú",
    "ü",
    "ñ",
    "¡",
    "¿",
)
ORIGINAL_ASCII_CHARS = (chr(i) for i in range(32, 127))
ORIGINAL_CHARACTER_SET = "".join(ORIGINAL_ASCII_CHARS) + "".join(ORIGINAL_UTF8_CHARS)

CHARS = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ÁÉÍÓÚÜÑáéíóúüñ¡¿"
ARTHUR_CHARACTER_SET = set(x for x in CHARS)

print("ARTHUR_CHARACTER_SET", len(CHARS), " - ", len(ARTHUR_CHARACTER_SET), "\n\n")


def find_unused_color(pixels) -> Tuple[int, int, int] | None:
    used_colors = set()
    for pixel in pixels:
        if len(pixel) >= 3:
            used_colors.add((pixel[0], pixel[1], pixel[2]))

    for r in range(256):
        for g in range(256):
            for b in range(256):
                if (r, g, b) not in used_colors:
                    return (r, g, b)

    return None


def convert_png_to_bmp(png_path: str, bmp_path: str, color_depth: int = 16):
    if color_depth not in [16, 256]:
        raise ValueError("color_depth must be either 16 or 256")

    img = Image.open(png_path).convert("RGBA")

    unused_color = find_unused_color(img.getdata())

    if not unused_color:
        raise ValueError(f"Could not find an unused color in {png_path}")

    transparent_indexes = [i for i, pixel in enumerate(img.getdata()) if pixel[3] == 0]  # type: ignore

    img = img.convert("RGB").quantize(colors=color_depth)
    palette = img.getpalette()

    if not palette:
        raise ValueError(f"Could not get palette from image {png_path}")

    new_palette = [unused_color[0], unused_color[1], unused_color[2]] + palette[
        : 3 * (color_depth - 1)
    ]
    img.putpalette(new_palette)

    img_data = img.getdata()
    shifted_data = [1 if pixel == 0 else pixel + 1 for pixel in img_data]
    for i in transparent_indexes:
        shifted_data[i] = 0
    img.putdata(shifted_data)

    img.info["transparency"] = 0

    img.save(bmp_path, format="BMP")


def parse_font_txt(txt_path: str) -> Dict:
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    width_match = re.search(r"Character width:\s*(\d+)", content)
    char_width = int(width_match.group(1)) if width_match else None

    height_match = re.search(r"Character height:\s*(\d+)", content)
    char_height = int(height_match.group(1)) if height_match else None

    charset_match = re.search(r"Character set:\s*\n(.+?)\n\n", content, re.DOTALL)
    charset = charset_match.group(1).strip() if charset_match else ""

    spacing_data = None
    spacing_match = re.search(r"Spacing data:\s*(\[\[.*?\]\])", content, re.DOTALL)
    if spacing_match:
        try:
            spacing_data = ast.literal_eval(spacing_match.group(1))
        except:
            print(f"Warning: Could not parse spacing data from {txt_path}")

    char_spacing = None
    char_spacing_match = re.search(r"Character spacing:\s*(-?\d+)", content)
    if char_spacing_match:
        char_spacing = int(char_spacing_match.group(1))

    return {
        "char_width": char_width,
        "char_height": char_height,
        "charset": charset,
        "spacing_data": spacing_data,
        "char_spacing": char_spacing,
    }


def create_character_width_map(spacing_data: List) -> Dict[str, int]:
    char_widths = {}
    if spacing_data:
        for width, chars in spacing_data:
            for char in chars:
                char_widths[char] = width
    return char_widths


def extract_characters_from_grid(
    png_path: str, charset: str, tile_width: int, tile_height: int
) -> Tuple[List[Image.Image], str, int, int]:
    img = Image.open(png_path).convert("RGBA")

    cols = 26
    rows = 11

    characters = []
    filtered_charset = []
    char_index = 0
    max_content_width = 0
    max_content_height = 0

    for row in range(rows):
        for col in range(cols):
            if char_index >= len(charset):
                break
            if charset[char_index] == " ":
                continue

            char = charset[char_index]

            x = col * tile_width
            y = row * tile_height
            char_img = img.crop((x, y, x + tile_width, y + tile_height))

            if char in CHARS:
                if char_index < len(charset) + 1:
                    bbox = char_img.getbbox()
                    if bbox:
                        # char_img = char_img.crop(bbox)
                        content_width = bbox[2] - bbox[0]
                        content_height = bbox[3] - bbox[1]
                        max_content_width = max(max_content_width, content_width)
                        max_content_height = max(max_content_height, content_height)

                characters.append(char_img)
                filtered_charset.append(char)

            char_index += 1

    characters = sorted(
        characters,
        key=lambda _x: CHARS.index(filtered_charset[characters.index(_x)]),
        reverse=False,
    )
    filtered_charset = sorted(
        filtered_charset, key=lambda _x: CHARS.index(_x), reverse=False
    )

    return characters, "".join(filtered_charset), max_content_width, max_content_height


def round_up_to_gba_sprite_size(width: int, height: int) -> int:
    max_dim = max(width, height)

    if max_dim <= 8:
        return 8
    elif max_dim <= 16:
        return 16
    elif max_dim <= 32:
        return 32
    elif max_dim <= 64:
        return 64
    else:
        raise ValueError(
            f"Font dimensions {width}x{height} too large for GBA (max 64x64)"
        )


def create_vertical_strip(
    characters: List[Image.Image], target_width: int, target_height: int
) -> Image.Image:
    num_chars = len(characters)
    strip_height = target_height * num_chars

    strip = Image.new("RGBA", (target_width, strip_height), (0, 0, 0, 0))

    for i, char_img in enumerate(characters):
        y_pos = i * target_height
        x_offset = 0
        y_offset = 0

        strip.paste(char_img, (x_offset, y_pos + y_offset), char_img)

    return strip


def generate_json_file(output_path: str, sprite_width: int, sprite_height: int):
    data = {"type": "sprite", "height": sprite_height, "width": sprite_width}
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)


def generate_cpp_header(
    output_path: str,
    font_name: str,
    size_name: str,
    charset: str,
    char_widths: Dict[str, int],
    sprite_item_name: str,
):
    utf8_chars = []
    utf8_widths = []

    ascii_widths = []
    for ascii_code in range(32, 127):
        char = chr(ascii_code)
        if char in charset and char in char_widths:
            ascii_widths.append((ascii_code, char, char_widths[char]))
        else:
            ascii_widths.append((ascii_code, char, 8))

    for char in ORIGINAL_UTF8_CHARS:
        utf8_chars.append(char)
        if char in charset and char in char_widths:
            utf8_widths.append(char_widths[char])
        else:
            # use default width of 8 for missing UTF-8 characters
            utf8_widths.append(8)

    guard = f"{font_name.upper()}_{size_name.upper()}_FONT_HPP"

    lines = [
        "//",
        "// Auto-generated Butano font header",
        "//",
        "",
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        '#include "bn_sprite_font.h"',
        f'#include "bn_sprite_items_{sprite_item_name}.h"',
        '#include "bn_utf8_characters_map.h"',
        "namespace fonts {",
    ]

    if utf8_chars:
        utf8_chars_formatted = ", ".join([f'"{char}"' for char in utf8_chars])
        lines.append(
            f"constexpr bn::utf8_character {font_name}_{size_name}_sprite_font_utf8_characters[] = {{"
        )
        lines.append(f"    {utf8_chars_formatted}")
        lines.append("};")
        lines.append("")

    lines.append(
        f"constexpr signed char {font_name}_{size_name}_sprite_font_character_widths[] = {{"
    )
    for ascii_code, char, width in ascii_widths:
        char_display = char
        if char == "\\":
            char_display = "[backslash]"
        elif char == "'":
            char_display = "\\'"
        elif char == '"':
            char_display = '\\"'
        lines.append(f"    {width}, // {ascii_code} {char_display}")

    for i, width in enumerate(utf8_widths):
        lines.append(f"    {width}, // {utf8_chars[i]}")

    lines.append("};")
    lines.append("")

    lines.extend(
        [
            f"constexpr bn::span<const bn::utf8_character> {font_name}_{size_name}_sprite_font_utf8_characters_span(",
            f"    {font_name}_{size_name}_sprite_font_utf8_characters",
            ");",
            "",
            f"constexpr auto {font_name}_{size_name}_sprite_font_utf8_characters_map =",
            f"    bn::utf8_characters_map<{font_name}_{size_name}_sprite_font_utf8_characters_span>();",
            "",
        ]
    )

    lines.extend(
        [
            f"constexpr bn::sprite_font {font_name}_{size_name}_sprite_font(",
            f"    bn::sprite_items::{sprite_item_name}, {font_name}_{size_name}_sprite_font_utf8_characters_map.reference(),",
            f"    {font_name}_{size_name}_sprite_font_character_widths",
        ]
    )

    lines.extend([");", "}", f"#endif //{guard}", ""])

    with open(output_path, "w") as f:
        f.write("\n".join(lines))


def convert_font(
    font_dir: str | Path,
    graphics_dir: str | Path,
    includes_dir: str | Path,
    font_name: str | None = None,
    target_sprite_size: int | None = None,
):
    font_dir = Path(font_dir)
    graphics_dir = Path(graphics_dir)
    includes_dir = Path(includes_dir)

    if not font_name:
        font_name = font_dir.name
        if "_v" in font_name:
            font_name = font_name.rsplit("_v", 1)[0]
        font_name = re.sub(r"_\d+$", "", font_name)

    txt_files = list(font_dir.glob("*.txt"))
    png_files = list(font_dir.glob("*.png"))

    if not txt_files or not png_files:
        raise ValueError(f"Could not find .txt or .png file in {font_dir}")

    txt_path = txt_files[0]
    png_path = png_files[0]

    print(f"Converting font: {font_name}")
    print(f"  Source: {font_dir}")
    print(f"  TXT: {txt_path.name}")
    print(f"  PNG: {png_path.name}")

    metadata = parse_font_txt(str(txt_path))
    char_width = metadata["char_width"]
    char_height = metadata["char_height"]
    charset = metadata["charset"]
    spacing_data = metadata["spacing_data"]

    print(f"  Character count: {len(charset)}")

    char_widths = create_character_width_map(spacing_data) if spacing_data else {}

    characters, filtered_charset, max_content_width, max_content_height = (
        extract_characters_from_grid(str(png_path), charset, char_width, char_height)
    )

    print(filtered_charset)
    print(
        f"  Extracted {len(characters)} characters (filtered from {len(charset)} total)"
    )

    actual_width = (
        max_content_width if char_width > max_content_width > 0 else char_width
    )
    actual_height = (
        max_content_height if char_height > max_content_height > 0 else char_height
    )

    print(f"  Tile size (from TXT): {char_width}x{char_height}")
    print(f"  Actual content size (Arthur chars only): {actual_width}x{actual_height}")

    if not target_sprite_size:
        target_sprite_size = round_up_to_gba_sprite_size(actual_width, actual_height)

    target_width = target_sprite_size
    target_height = target_sprite_size

    print(f"  Target sprite size: {target_width}x{target_height}")

    strip = create_vertical_strip(characters, target_width, target_height)
    print(f"  Created vertical strip: {strip.width}x{strip.height}")

    graphics_dir.mkdir(parents=True, exist_ok=True)
    includes_dir.mkdir(parents=True, exist_ok=True)

    size_name = f"{target_width}x{target_height}"
    sprite_item_name = f"{font_name.replace('_', '')}{size_name.replace('x', 'x')}"

    temp_png = graphics_dir / f"{sprite_item_name}_temp.png"
    strip.save(str(temp_png))

    bmp_path = graphics_dir / f"{sprite_item_name}.bmp"
    convert_png_to_bmp(str(temp_png), str(bmp_path), color_depth=16)
    temp_png.unlink()  # remove temp file
    print(f"  Created: {bmp_path}")

    json_path = graphics_dir / f"{sprite_item_name}.json"
    generate_json_file(str(json_path), target_width, target_height)
    print(f"  Created: {json_path}")

    hpp_path = includes_dir / f"{font_name}_{size_name}_font.hpp"
    generate_cpp_header(
        str(hpp_path),
        font_name,
        size_name,
        filtered_charset,
        char_widths,
        sprite_item_name,
    )
    print(f"  Created: {hpp_path}")

    print(f"✓ Conversion complete!")
    return {
        "font_name": font_name,
        "size_name": size_name,
        "sprite_item_name": sprite_item_name,
        "bmp_path": bmp_path,
        "json_path": json_path,
        "hpp_path": hpp_path,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python convert_font_to_butano.py <font_directory> [graphics_dir] [includes_dir] [font_name]"
        )
        print("\nExample:")
        print(
            "  python convert_font_to_butano.py absolute_10_v1 butano-fonts/graphics butano-fonts/includes"
        )
        sys.exit(1)

    font_dir = sys.argv[1]
    dir_name = Path(font_dir).name
    if "_v" in dir_name:
        dir_name = dir_name.rsplit("_v", 1)[0]
    default_name = re.sub(r"_\d+$", "", dir_name)
    graphics_dir = sys.argv[2] if len(sys.argv) > 2 else "butano-fonts/graphics"
    includes_dir = sys.argv[3] if len(sys.argv) > 3 else "butano-fonts/includes"
    font_name = sys.argv[4] if len(sys.argv) > 4 else default_name

    result = convert_font(font_dir, graphics_dir, includes_dir, font_name)

    if result is None:
        exit(1)
