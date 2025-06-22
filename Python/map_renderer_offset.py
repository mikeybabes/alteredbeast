import os
import sys
import math
from PIL import Image

def render_maps(map_file, char_file, palette_file, output_dir, char_offset_hex="0", screens_wide=5):
    """
    Render all map screens to PNGs with:
    - Character file offset support (hex)
    - Configurable screens per wide image (default:5)
    - Proper palette banking: (tile_number & 0x1FFF) // 64
    """
    # Constants
    SCREEN_WIDTH = 64
    SCREEN_HEIGHT = 32
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

    # Calculate number of screens and wide images needed
    screen_size_bytes = SCREEN_WIDTH * SCREEN_HEIGHT * 2
    total_screens = len(map_data) // screen_size_bytes
    wide_images_needed = math.ceil(total_screens / screens_wide)
    print(f"Rendering {total_screens} screens into {wide_images_needed} wide images")
    print(f"Using character offset: {char_offset:04X}h")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Process in chunks of [screens_wide] screens
    for wide_img_num in range(wide_images_needed):
        start_screen = wide_img_num * screens_wide
        end_screen = min((wide_img_num + 1) * screens_wide, total_screens)
        screens_in_wide = end_screen - start_screen

        # Create wide output image
        wide_width = screens_in_wide * SCREEN_WIDTH * 8
        wide_height = SCREEN_HEIGHT * 8
        wide_img = Image.new('RGBA', (wide_width, wide_height))
        pixels = wide_img.load()
        invalid_tiles = 0

        # Process each screen in this wide image
        for screen_offset in range(screens_in_wide):
            screen_num = start_screen + screen_offset
            screen_data_offset = screen_num * screen_size_bytes
            screen_x_offset = screen_offset * SCREEN_WIDTH * 8

            # Process each tile in screen
            for tile_idx in range(SCREEN_WIDTH * SCREEN_HEIGHT):
                # Read map entry (little-endian word)
                entry_offset = screen_data_offset + tile_idx * 2
                if entry_offset + 1 >= len(map_data):
                    print(f"Warning: Map data truncated at offset {entry_offset:X}h")
                    continue
                
                tile_number = map_data[entry_offset] | (map_data[entry_offset + 1] << 8)
                banked_tile = tile_number & BANK_MASK

                # Calculate character data location with offset
                effective_char_offset = char_offset + (banked_tile * CHAR_SIZE)
                
                if effective_char_offset + CHAR_SIZE > len(chars):
                    invalid_tiles += 1
                    print(f"Invalid tile at: WideImg {wide_img_num} "
                          f"Screen {screen_num} "
                          f"Pos [{tile_idx%SCREEN_WIDTH:X},{tile_idx//SCREEN_HEIGHT:X}] "
                          f"Map offset {entry_offset:X}h "
                          f"Tile number {tile_number:X}h "
                          f"Char offset: {effective_char_offset:X}h")
                    continue

                # Calculate palette group
                palette_group = banked_tile // CHARS_PER_PALETTE
                palette_offset = palette_group * COLORS_PER_PALETTE * BYTES_PER_COLOR

                # Get palette colors
                palette = []
                for i in range(COLORS_PER_PALETTE):
                    offset = palette_offset + i*BYTES_PER_COLOR
                    if offset + 2 < len(palette_data):
                        r, g, b = palette_data[offset:offset+3]
                        a = 0 if i == 0 else 255
                        palette.append((r, g, b, a))
                    else:
                        palette.append((255, 0, 255, 255))

                # Calculate positions
                tile_x = screen_x_offset + (tile_idx % SCREEN_WIDTH) * 8
                tile_y = (tile_idx // SCREEN_WIDTH) * 8

                # Render character
                for byte_pos in range(CHAR_SIZE):
                    byte = chars[effective_char_offset + byte_pos]
                    px = (byte_pos % 4) * 2
                    py = byte_pos // 4

                    for nibble_pos, shift in [(0, 4), (1, 0)]:
                        pixel_val = (byte >> shift) & 0x07
                        pixels[tile_x+px+nibble_pos, tile_y+py] = palette[pixel_val]

        # Save wide image
        output_path = os.path.join(output_dir, f"wide_{wide_img_num:02d}.png")
        wide_img.save(output_path)
        print(f"Saved {output_path} (screens {start_screen}-{end_screen-1}, skipped {invalid_tiles} tiles)")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python map_renderer.py map.bin chars.bin palette.bin output_dir [char_offset] [screens_wide]")
        print("Example (default): python map_renderer.py map.bin chars.bin palette.bin output/")
        print("Example (with offset): python map_renderer.py map.bin chars.bin palette.bin output/ 1000")
        print("Example (custom width): python map_renderer.py map.bin chars.bin palette.bin output/ 0 3")
        sys.exit(1)
    
    map_file = sys.argv[1]
    char_file = sys.argv[2]
    palette_file = sys.argv[3]
    output_dir = sys.argv[4]
    char_offset_hex = sys.argv[5] if len(sys.argv) > 5 else "0"
    screens_wide = int(sys.argv[6]) if len(sys.argv) > 6 else 5
    
    render_maps(map_file, char_file, palette_file, output_dir, char_offset_hex, screens_wide)