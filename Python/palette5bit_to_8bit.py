import sys

def pal5bit(val):
    """Convert a 5-bit value (0-31) to 8-bit (0-255) as in MAME."""
    return ((val & 0x1F) << 3) | ((val & 0x1F) >> 2)

def sega16_palette_decode(word):
    # Replicate the MAME logic for System 16B palette RAM
    r = ((word >> 12) & 0x01) | ((word << 1) & 0x1e)
    g = ((word >> 13) & 0x01) | ((word >> 3) & 0x1e)
    b = ((word >> 14) & 0x01) | ((word >> 7) & 0x1e)
    return pal5bit(r), pal5bit(g), pal5bit(b)

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} input.bin output.pal")
        sys.exit(1)

    infile = sys.argv[1]
    outfile = sys.argv[2]

    rgb_bytes = bytearray()
    with open(infile, "rb") as f:
        while True:
            bytes2 = f.read(2)
            if len(bytes2) < 2:
                break
            word = int.from_bytes(bytes2, "big")
            r, g, b = sega16_palette_decode(word)
            rgb_bytes.extend([r, g, b])

    with open(outfile, "wb") as f:
        f.write(rgb_bytes)

    print(f"Converted {len(rgb_bytes)//3} entries from {infile} to {outfile}")

if __name__ == "__main__":
    main()
