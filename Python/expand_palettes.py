#!/usr/bin/env python3
import sys
from pathlib import Path

def expand_palettes(input_path, output_path):
    """
    Read an input binary file containing 14-color palettes (RGB triples) per chunk,
    report how many palettes were found, and write an output file where each
    palette is expanded to 16 colors by injecting a black (0,0,0) at the start
    and end of each 14-color block.
    """
    data = Path(input_path).read_bytes()
    chunk_size = 14 * 3  # 42 bytes per palette

    if len(data) % chunk_size != 0:
        print(f"Error: input size {len(data)} is not a multiple of {chunk_size}.", file=sys.stderr)
        sys.exit(1)

    num_palettes = len(data) // chunk_size
    print(f"Found {num_palettes} palettes in '{input_path}'.")  # ← new reporting line

    black = bytes([0, 0, 0])
    out = bytearray()

    for i in range(num_palettes):
        start = i * chunk_size
        palette = data[start:start + chunk_size]
        out.extend(black)      # new color 0
        out.extend(palette)    # original 14 colors
        out.extend(black)      # new color 15

    Path(output_path).write_bytes(out)
    print(f"Expanded to 16 colors each, wrote {len(out)} bytes to '{output_path}'.")

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input.bin output.bin")
        sys.exit(1)
    expand_palettes(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
