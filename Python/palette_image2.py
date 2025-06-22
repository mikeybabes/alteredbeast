from PIL import Image, ImageDraw, ImageFont
import sys
import os
import argparse
import math

def load_palettes(input_file, n_colors):
    with open(input_file, "rb") as f:
        data = f.read()
    if len(data) % (n_colors*3) != 0:
        raise ValueError(f"Input size is not a multiple of {n_colors*3} (colors × 3 bytes)")
    n_palettes = len(data) // (n_colors*3)
    palettes = []
    for p in range(n_palettes):
        base = p * n_colors * 3
        palette = []
        for c in range(n_colors):
            off = base + c * 3
            r, g, b = data[off], data[off+1], data[off+2]
            palette.append((r, g, b))
        palettes.append(palette)
    return palettes

def main(input_file, output_file, columns):
    n_colors = 14
    img_width = 3840
    padding_top = 80
    index_width = 130
    col_gap = 32
    row_gap = 8
    extra_bottom = 16  # <--- Add extra height at bottom

    usable_width = img_width - (col_gap * (columns - 1))
    block_width = usable_width // columns
    swatch_size = (block_width - index_width) // n_colors

    palettes = load_palettes(input_file, n_colors)
    n_palettes = len(palettes)
    n_rows = math.ceil(n_palettes / columns)

    # Font sizes
    font_hex_sz = int(swatch_size * 0.65)
    font_dec_sz = int(swatch_size * 0.35)
    font_top_sz = int(swatch_size * 0.38)

    try:
        font_hex = ImageFont.truetype("arial.ttf", font_hex_sz)
        font_dec = ImageFont.truetype("arial.ttf", font_dec_sz)
        font_top = ImageFont.truetype("arial.ttf", font_top_sz)
    except IOError:
        font_hex = ImageFont.load_default()
        font_dec = ImageFont.load_default()
        font_top = ImageFont.load_default()

    block_height = swatch_size
    img_height = padding_top + n_rows * block_height + row_gap * (n_rows - 1) + extra_bottom  # <--- Add here

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Draw color numbers at the top of each block
    for col in range(columns):
        x0 = col * (block_width + col_gap)
        for c in range(n_colors):
            xx = x0 + index_width + c * swatch_size + swatch_size // 2
            y = padding_top // 2 - font_top_sz // 2
            label = f"{c:X}"
            bbox = draw.textbbox((0,0), label, font=font_top)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((xx - w//2, y), label, fill="black", font=font_top)

    # Draw palettes
    for i, palette in enumerate(palettes):
        block_col = i // n_rows
        block_row = i % n_rows
        x0 = block_col * (block_width + col_gap)
        y0 = padding_top + block_row * (block_height + row_gap)

        # Palette index (hex & decimal)
        hex_txt = f"${i:02X}"
        dec_txt = f"{i:3d}"
        bbox_hex = draw.textbbox((0,0), hex_txt, font=font_hex)
        w_hex, h_hex = bbox_hex[2] - bbox_hex[0], bbox_hex[3] - bbox_hex[1]
        bbox_dec = draw.textbbox((0,0), dec_txt, font=font_dec)
        w_dec, h_dec = bbox_dec[2] - bbox_dec[0], bbox_dec[3] - bbox_dec[1]
        draw.text((x0 + index_width//2 - w_hex//2, y0 + 5), hex_txt, fill="black", font=font_hex)
        draw.text((x0 + index_width//2 - w_dec//2, y0 + 7 + h_hex), dec_txt, fill="black", font=font_dec)
        for c in range(n_colors):
            color = palette[c]
            x = x0 + index_width + c * swatch_size
            draw.rectangle([x, y0, x + swatch_size - 1, y0 + swatch_size - 1], fill=color)

    img.save(output_file)
    print(f"Saved: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a palette PNG from palettes with 14 colors each (3 bytes RGB).")
    parser.add_argument("input_file", help="Binary palette file")
    parser.add_argument("output_file", help="Output PNG filename")
    parser.add_argument("--columns", type=int, default=1, help="Number of columns (default: 1)")
    args = parser.parse_args()
    main(args.input_file, args.output_file, args.columns)
