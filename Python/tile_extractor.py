import sys
import os
from struct import unpack

def extract_tile_blocks(input_file, base_name, start_offset_hex, count):
    """
    Extract and save tile data blocks with dimensions in filenames
    - base_name: Output filename prefix (e.g., "level1")
    - start_offset_hex: Starting position in hex
    - count: Number of blocks to extract
    """
    try:
        with open(input_file, 'rb') as f:
            start_offset = int(start_offset_hex, 16)
            f.seek(start_offset)
            
            for i in range(count):
                # Read header
                header = f.read(6)
                if len(header) < 6:
                    print(f"Error: End of file at block {i}")
                    break
                
                # Parse dimensions
                width = unpack('>H', header[2:4])[0] + 1  # +1 as per your formula
                height = unpack('>H', header[4:6])[0] + 1
                data_size = width * height * 2
                
                # Read tile data
                tile_data = f.read(data_size)
                if len(tile_data) < data_size:
                    print(f"Error: Tile data truncated in block {i}")
                    break
                
                # Generate filename
                output_file = f"{base_name}_{i+1}_{width}x{height}.bin"
                
                # Save data
                with open(output_file, 'wb') as out:
                    out.write(tile_data)
                
                print(f"Saved {output_file} ({width}x{height}, {data_size} bytes)")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
    except ValueError:
        print(f"Error: Invalid offset '{start_offset_hex}'")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python tile_extractor.py input.bin base_name start_offset count")
        print("Example: python tile_extractor.py rom.bin level1 278B8 7")
        sys.exit(1)
    
    input_file = sys.argv[1]
    base_name = sys.argv[2]
    start_offset = sys.argv[3]
    count = int(sys.argv[4])
    
    extract_tile_blocks(input_file, base_name, start_offset, count)