import argparse
from PIL import Image, ImageDraw, ImageFont
import sys

def read_word(data, offset):
    """Read 16-bit big-endian word (68000 format)"""
    return (data[offset] << 8) | data[offset+1]

def read_long(data, offset):
    """Read 32-bit big-endian long word (68000 format)"""
    return (data[offset] << 24) | (data[offset+1] << 16) | \
           (data[offset+2] << 8) | data[offset+3]

def get_sprite_info(code_bin, sprite_num):
    """Get verified sprite info from ROM"""
    MASTER_TABLE_OFFSET = 0x255E0
    entry_offset = MASTER_TABLE_OFFSET + (sprite_num * 6)
    size_offset = read_word(code_bin, entry_offset)
    data_ptr = read_long(code_bin, entry_offset + 2)

    size_ptr = MASTER_TABLE_OFFSET + size_offset
    ysize = code_bin[size_ptr]
    xsize_words = code_bin[size_ptr + 1]
    
    return xsize_words * 2, ysize, data_ptr + xsize_words

def read_sprite_data(sprite_bin, offset, xsize, ysize):
    """Read 4-bit sprite data (2 pixels per byte)"""
    sprite_size = (xsize * ysize + 1) // 2
    return sprite_bin[offset:offset + sprite_size]

def read_palette(palette_bin, palette_num):
    """Read 16-color palette (8-bit RGB)"""
    palette_offset = palette_num * 16 * 3
    palette_bytes = palette_bin[palette_offset:palette_offset + 16 * 3]
    return [(palette_bytes[i*3], palette_bytes[i*3+1], palette_bytes[i*3+2]) 
            for i in range(16)]

def load_palette_assignments(palette_file):
    """Load sprite to palette mappings from text file"""
    palette_map = {}
    with open(palette_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(',')
                sprite_num = int(parts[0], 16)
                palette_map[sprite_num] = [int(p, 16) for p in parts[1:]] if len(parts) > 1 else [0]
    return palette_map

def create_sprite_image(sprite_bytes, palette, xsize, ysize):
    """Create image with proper transparency handling"""
    img = Image.new('RGBA', (xsize, ysize))
    pixels = []
    
    for i in range(xsize * ysize):
        byte_pos = i // 2
        if i % 2 == 0:  # High nibble
            color_index = (sprite_bytes[byte_pos] >> 4) & 0x0F
        else:  # Low nibble
            color_index = sprite_bytes[byte_pos] & 0x0F
        
        if color_index in (0, 15):
            pixels.append((0, 0, 0, 0))  # Transparent
        else:
            r, g, b = palette[color_index]
            pixels.append((r, g, b, 255))
    
    img.putdata(pixels)
    return img

def create_sprite_atlas(code_bin, sprite_bin, palette_bin, output_file, palette_map, padding=4, overlay_file=None, start_sprite=0, end_sprite=None):
    """Create optimized sprite atlas with all palette variations"""
    with open(code_bin, 'rb') as f:
        code_data = f.read()
    with open(sprite_bin, 'rb') as f:
        sprite_data = f.read()
    with open(palette_bin, 'rb') as f:
        palette_data = f.read()
    
    sprites = []
    if end_sprite is None:
        end_sprite = max(palette_map.keys()) if palette_map else 647
    
    for sprite_num in range(start_sprite, end_sprite + 1):
        try:
            xsize, ysize, data_offset = get_sprite_info(code_data, sprite_num)
            if xsize > 0 and ysize > 0:
                palettes = palette_map.get(sprite_num, [0])
                for palette_num in palettes:
                    sprites.append((sprite_num, xsize, ysize, data_offset, palette_num))
        except (IndexError, TypeError):
            continue
    
    # Calculate atlas dimensions including label space
    label_height = 14 if overlay_file else 0
    row_width = 0
    max_row_width = 0
    current_row_height = 0
    total_height = 0
    
    for _, xsize, ysize, _, _ in sprites:
        if row_width + xsize + padding > 4096:
            max_row_width = max(max_row_width, row_width)
            total_height += current_row_height + padding + label_height
            row_width = 0
            current_row_height = 0
        
        row_width += xsize + padding
        current_row_height = max(current_row_height, ysize)
    
    max_row_width = max(max_row_width, row_width)
    total_height += current_row_height + label_height
    
    atlas = Image.new('RGBA', (max_row_width, total_height), (0, 0, 0, 0))
    
    overlay = None
    if overlay_file:
        overlay = Image.new('RGBA', (max_row_width, total_height), (0, 0, 0, 0))
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(overlay)
    
    x_pos, y_pos = 0, 0
    current_row_height = 0
    row_start_y = 0
    row_sprites = []
    last_sprite_num = None
    
    for sprite_num, xsize, ysize, data_offset, palette_num in sprites:
        if x_pos + xsize > max_row_width:
            for sx, sy, ssprite_num, ssprite_img, spalette_num in row_sprites:
                sprite_y = row_start_y + (current_row_height - ssprite_img.height)
                atlas.paste(ssprite_img, (sx, sprite_y))
                
                if overlay:
                    if ssprite_num != last_sprite_num:
                        hex_code = f"{ssprite_num:X}:{spalette_num:02X}"
                    else:
                        hex_code = f"{spalette_num:02X}"
                    
                    last_sprite_num = ssprite_num
                    
                    bbox = draw.textbbox((0, 0), hex_code, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_x = sx + (ssprite_img.width - text_width) // 2
                    text_y = row_start_y + current_row_height + 2
                    
                    for ox, oy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                        draw.text((text_x+ox, text_y+oy), hex_code, font=font, fill=(0,0,0,255))
                    draw.text((text_x, text_y), hex_code, font=font, fill=(255,255,255,255))
            
            x_pos = 0
            y_pos += current_row_height + padding + label_height
            row_start_y = y_pos
            current_row_height = 0
            row_sprites = []
            last_sprite_num = None
        
        try:
            palette = read_palette(palette_data, palette_num)
            sprite_bytes = read_sprite_data(sprite_data, data_offset, xsize, ysize)
            sprite_img = create_sprite_image(sprite_bytes, palette, xsize, ysize)
            
            row_sprites.append((x_pos, y_pos, sprite_num, sprite_img, palette_num))
            current_row_height = max(current_row_height, ysize)
            x_pos += xsize + padding
            
        except Exception as e:
            print(f"Skipping sprite {sprite_num}: {str(e)}")
    
    for sx, sy, ssprite_num, ssprite_img, spalette_num in row_sprites:
        sprite_y = row_start_y + (current_row_height - ssprite_img.height)
        atlas.paste(ssprite_img, (sx, sprite_y))
        
        if overlay:
            if ssprite_num != last_sprite_num:
                hex_code = f"{ssprite_num:X}:{spalette_num:02X}"
            else:
                hex_code = f"{spalette_num:02X}"
            
            last_sprite_num = ssprite_num
            
            bbox = draw.textbbox((0, 0), hex_code, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = sx + (ssprite_img.width - text_width) // 2
            text_y = row_start_y + current_row_height + 2
            
            for ox, oy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                draw.text((text_x+ox, text_y+oy), hex_code, font=font, fill=(0,0,0,255))
            draw.text((text_x, text_y), hex_code, font=font, fill=(255,255,255,255))
    
    atlas.save(output_file)
    if overlay:
        overlay.save(overlay_file)
    
    print(f"Created atlas with {len(sprites)} sprite variations (sprites {start_sprite:X}-{end_sprite:X})")
    print(f"Dimensions: {max_row_width}x{total_height}")
    if overlay:
        print(f"Code overlay saved to: {overlay_file}")

def main():
    parser = argparse.ArgumentParser(description='Create sprite atlas with palette variations')
    parser.add_argument('code_bin', help='Game code binary')
    parser.add_argument('sprite_bin', help='Sprite data binary')
    parser.add_argument('palette_bin', help='Palette binary')
    parser.add_argument('palette_txt', help='Sprite palette assignments file')
    parser.add_argument('output_png', help='Output PNG file')
    parser.add_argument('--padding', type=int, default=4, help='Padding between sprites (default: 4)')
    parser.add_argument('--overlay', help='Generate code overlay PNG')
    parser.add_argument('--start', type=int, default=0, help='First sprite number to include (default: 0)')
    parser.add_argument('--end', type=int, help='Last sprite number to include (default: all defined sprites)')
    
    args = parser.parse_args()
    palette_map = load_palette_assignments(args.palette_txt)
    
    create_sprite_atlas(
        args.code_bin,
        args.sprite_bin,
        args.palette_bin,
        args.output_png,
        palette_map,
        padding=args.padding,
        overlay_file=args.overlay,
        start_sprite=args.start,
        end_sprite=args.end
    )

if __name__ == '__main__':
    main()