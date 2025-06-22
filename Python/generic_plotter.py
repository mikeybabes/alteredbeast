import os
import sys
import math
from PIL import Image

def plot_map_with_offset(map_file, char_file, palette_file, output_file, 
                        width=64, height=None, char_offset_hex=0):
    """
    Generic map plotter with configurable dimensions and character file offset:
    - width: Map width in tiles (default:64)
    - height: Map height in tiles (auto-calculated if None)
    - char_offset_hex: Offset into character file in hex (default:0)
    - Palette banking: (tile_number & 0x1FFF) // 64
    """
    # Constants
    TILE_SIZE = 8  # 8x8 pixels
    CHAR_SIZE = 32  # 8x8 4bpp
    BANK_MASK = 0x1FFF
    CHARS_PER_PALETTE = 64
    COLORS_PER_PALETTE = 8
    BYTES_PER_COLOR = 3  # RGB

    # Convert hex offset to decimal
    try:
        char_offset = int(char_offset_hex, 16)
    except ValueError:
        print(f"Error: Invalid hex offset '{char_offset_hex}'")
        return

    # Load all data
    try:
        with open(char_file, 'rb') as f:
            chars = f.read()
        with open(palette_file, 'rb') as f:
            palette_data = f.read()
        with open(map_file, 'rb') as f:
            map_data = f.read()
    except FileNotFoundError as e:
        print(f"Error reading files: {e}")
        return

    # Calculate height if not specified
    if height is None:
        height = len(map_data) // 2 // width
        print(f"Auto-calculated height: {height} tiles")

    # Validate dimensions
    expected_size = width * height * 2
    if len(map_data) < expected_size:
        print(f"Warning: Map data smaller than expected ({len(map_data)} < {expected_size} bytes)")
    elif len(map_data) > expected_size:
        print(f"Warning: Map data larger than expected, truncating ({len(map_data)} > {expected_size} bytes)")

    # Create output image
    img_width = width * TILE_SIZE
    img_height = height * TILE_SIZE
    img = Image.new('RGBA', (img_width, img_height))
    pixels = img.load()

    # Process each tile
    for tile_idx in range(width * height):
        entry_offset = tile_idx * 2
        if entry_offset + 1 >= len(map_data):
            break  # Handle truncated data

        # Read tile number (little-endian)
        tile_number = map_data[entry_offset] | (map_data[entry_offset + 1] << 8)
        banked_tile = tile_number & BANK_MASK

        # Calculate character data location with offset
        effective_char_offset = char_offset + (banked_tile * CHAR_SIZE)
        
        if effective_char_offset + CHAR_SIZE > len(chars):
            print(f"Invalid tile at position {tile_idx} (offset {entry_offset:04X}h): "
                  f"Tile {tile_number:04X}h (Banked: {banked_tile:04X}h) "
                  f"Char offset: {effective_char_offset:04X}h")
            continue

        # Calculate palette group
        palette_group = banked_tile // CHARS_PER_PALETTE
        palette_offset = palette_group * COLORS_PER_PALETTE * BYTES_PER_COLOR

        # Get palette colors
        palette = []
        for i in range(COLORS_PER_PALETTE):
            offset = palette_offset + i * BYTES_PER_COLOR
            if offset + 2 < len(palette_data):
                r, g, b = palette_data[offset:offset+3]
                a = 0 if i == 0 else 255  # Transparent for color 0
                palette.append((r, g, b, a))
            else:
                palette.append((255, 0, 255, 255))  # Error color

        # Calculate position
        tile_x = (tile_idx % width) * TILE_SIZE
        tile_y = (tile_idx // width) * TILE_SIZE

        # Render character
        for byte_pos in range(CHAR_SIZE):
            byte = chars[effective_char_offset + byte_pos]
            px = (byte_pos % 4) * 2  # Two pixels per byte
            py = byte_pos // 4

            for nibble_pos, shift in [(0, 4), (1, 0)]:
                pixel_val = (byte >> shift) & 0x07
                if pixel_val >= len(palette):
                    pixel_val = 7  # Fallback
                pixels[tile_x + px + nibble_pos, tile_y + py] = palette[pixel_val]

    # Save output
    img.save(output_file)
    print(f"Saved map to {output_file} ({width}x{height} tiles, {img_width}x{img_height} pixels)")
    print(f"Used character offset: {char_offset:04X}h")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python offset_plotter.py map.bin chars.bin palette.bin output.png [width] [height] [char_offset]")
        print("Example (default 64-wide, no offset): python offset_plotter.py map.bin chars.bin palette.bin output.png")
        print("Example (128-wide with offset): python offset_plotter.py map.bin chars.bin palette.bin wide.png 128 None 1000")
        print("Example (specific dimensions): python offset_plotter.py map.bin chars.bin palette.bin custom.png 64 32 2000")
        sys.exit(1)
    
    map_file = sys.argv[1]
    char_file = sys.argv[2]
    palette_file = sys.argv[3]
    output_file = sys.argv[4]
    width = int(sys.argv[5]) if len(sys.argv) > 5 else 64
    height = int(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[6].lower() != "none" else None
    char_offset_hex = sys.argv[7] if len(sys.argv) > 7 else "0"
    
    plot_map_with_offset(map_file, char_file, palette_file, output_file, 
                        width, height, char_offset_hex)