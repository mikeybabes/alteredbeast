import os
import sys
import math
from PIL import Image

def generate_banked_atlas(char_file, palette_file, output_file):
    """
    Generate character atlas with proper palette banking
    Palette offset = (character_index & 0x1FFF) // 64
    """
    # Constants
    CHAR_SIZE = 32  # 8x8 pixels at 4bpp
    TILE_SIZE = 8
    GRID_WIDTH = 1920
    BANK_MASK = 0x1FFF  # Character index mask
    CHARS_PER_PALETTE = 64
    COLORS_PER_PALETTE = 8
    BYTES_PER_COLOR = 3  # RGB

    # Read files
    try:
        with open(char_file, 'rb') as f:
            char_data = f.read()
        with open(palette_file, 'rb') as f:
            palette_data = f.read()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # Calculate character count
    num_chars = len(char_data) // CHAR_SIZE
    print(f"Processing {num_chars} characters")
    print(f"Palette contains {len(palette_data)//BYTES_PER_COLOR} colors")

    # Grid layout (multiple of 16 columns)
    cols = (GRID_WIDTH // TILE_SIZE) // 16 * 16
    cols = max(16, cols)
    rows = math.ceil(num_chars / cols)

    # Create output image
    img = Image.new('RGBA', (cols*TILE_SIZE, rows*TILE_SIZE))
    pixels = img.load()

    # Process each character
    for char_idx in range(num_chars):
        # Apply banking mask
        banked_idx = char_idx & BANK_MASK
        palette_group = banked_idx // CHARS_PER_PALETTE
        palette_offset = palette_group * COLORS_PER_PALETTE * BYTES_PER_COLOR

        # Get palette colors (8 colors per group)
        palette = []
        for i in range(COLORS_PER_PALETTE):
            offset = palette_offset + i*BYTES_PER_COLOR
            if offset + 2 < len(palette_data):
                r, g, b = palette_data[offset:offset+3]
                a = 0 if i == 0 else 255  # Transparent for color 0
                palette.append((r, g, b, a))
            else:
                palette.append((255, 0, 255, 255))  # Error color

        # Character position in grid
        x = (char_idx % cols) * TILE_SIZE
        y = (char_idx // cols) * TILE_SIZE

        # Decode character data
        char_offset = char_idx * CHAR_SIZE
        for byte_pos in range(CHAR_SIZE):
            byte = char_data[char_offset + byte_pos]
            px = (byte_pos % 4) * 2  # Two pixels per byte
            py = byte_pos // 4

            # Unpack nibbles (only lower 3 bits used)
            for nibble_pos, shift in [(0, 4), (1, 0)]:
                pixel_val = (byte >> shift) & 0x07
                if pixel_val >= len(palette):
                    pixel_val = 7  # Fallback to last color
                pixels[x+px+nibble_pos, y+py] = palette[pixel_val]

    # Save output
    img.save(output_file)
    print(f"Saved banked character atlas to {output_file}")
    print(f"Used {palette_group + 1} palette groups")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python banked_atlas.py chars.bin palette.bin output.png")
        sys.exit(1)
    generate_banked_atlas(sys.argv[1], sys.argv[2], sys.argv[3])