#!/usr/bin/env python3
"""
decode_streams.py

Reads a single “input.bin” (a flat dump matching the arcade ROM’s memory map),
and for each of the eight level entries (as defined by the lookup table in the 68000 code),
decodes two RLE‐encoded bitplane streams (low and high) into separate uncompressed files:
  stream1low.bin, stream1high.bin, …, stream8low.bin, stream8high.bin.

Usage:
    python decode_streams.py input.bin

Each decoded stream will contain exactly 0x4FFF+1 bytes (20480 bytes), matching how
the original 68000 routines run until D1 underflows.
"""

import sys
import os

# =============================================================================
# Constants: table offsets and decoder parameters
# =============================================================================

# There are 8 entries in the lookup table, each 6 bytes long:
#   WORD “page” (ignored by decoder), then LONG offset → RLE data.
# The table itself begins at ROM offset 0x001CE2.
TABLE_BASE_OFFSET = 0x001CE2
ENTRY_SIZE = 6           # 2-byte page + 4-byte pointer
NUM_ENTRIES = 5          # the table has 8 entries but it seems missing, I think maybe the game would of had more levels!

# The eight RLE‐stream offsets (big‐endian LONGs) in the table at 0x1CE2…0x1D11:
LEVEL_OFFSETS = [
    0x00029E00,  # entry 0
    0x0002EF10,  # entry 1
    0x000324D0,  # entry 2
    0x000369C0,  # entry 3
    0x0003B0E0,  # entry 4
    0x000411A8,  # entry 5
    0x00044F20,  # entry 6
    0x00046F80,  # entry 7
]

# The initial D1 value used by both decoders; they decrement on each byte written
# and exit when D1 < 0. Per original 68000 logic, that yields exactly 0x4FFF+1 = 20480 writes.
INITIAL_D1 = 0x4FFF


# =============================================================================
# Helper functions: low‐plane and high‐plane decoders
# =============================================================================

def decode_low_plane(data: bytes, start_offset: int) -> (bytes, int):
    """
    Simulate the 68k routine at 0x0016BE…0x0016DC (low‐bitplane RLE decode).
    - Reads pairs of bytes [run_length, pixel_value] from data starting at start_offset.
    - For each pair, writes pixel_value (run_length + 1) times into the output.
    - Decrements D1 on every write; when D1 < 0, exit immediately.
    Returns:
      (decoded_bytes, bytes_consumed)
    """
    d1 = INITIAL_D1
    p = start_offset
    out = bytearray()

    while True:
        if p + 1 >= len(data):
            raise ValueError(f"Ran past end of data while decoding low plane (offset {hex(p)})")

        run_length = data[p]            # first byte  = D0
        pixel = data[p + 1]             # second byte = D2
        p += 2

        # Write (run_length + 1) copies of pixel
        # On each write, decrement d1; if d1 < 0, exit.
        for _ in range(run_length + 1):
            out.append(pixel)
            d1 -= 1
            if d1 < 0:
                # We’ve written enough bytes; return and report how many source bytes we consumed
                return bytes(out), p

    # (unreachable)


def decode_high_plane(data: bytes, start_offset: int) -> (bytes, int):
    """
    Simulate the 68k routine at 0x0016DE…0x001708 (high‐bitplane / literal decode).
    - Reads a single byte “value” from data:
      · If value != 0: write it once.
      · If value == 0:
          · Next byte = run_count.
          · If run_count == 0: write a single 0.
          · Else: write (run_count + 1) zero‐bytes.
    - On each write, decrement D1; when D1 < 0, exit immediately.
    Returns:
      (decoded_bytes, bytes_consumed)
    """
    d1 = INITIAL_D1
    p = start_offset
    out = bytearray()

    while True:
        if p >= len(data):
            raise ValueError(f"Ran past end of data while decoding high plane (offset {hex(p)})")

        val = data[p]   # first byte read into D0
        p += 1

        if val != 0:
            # literal nonzero → write once
            out.append(val)
            d1 -= 1
            if d1 < 0:
                return bytes(out), p
            continue

        # val == 0 → interpret next byte as run_count
        if p >= len(data):
            raise ValueError(f"Ran past end of data while reading run‐count (offset {hex(p)})")

        run_count = data[p]
        p += 1

        if run_count == 0:
            # single‐zero literal
            out.append(0)
            d1 -= 1
            if d1 < 0:
                return bytes(out), p
            continue

        # run_count > 0 → write (run_count + 1) zero‐bytes
        for _ in range(run_count + 1):
            out.append(0)
            d1 -= 1
            if d1 < 0:
                return bytes(out), p

        # loop back to read next “value”

    # (unreachable)


# =============================================================================
# Main script logic
# =============================================================================

def main():
    if len(sys.argv) != 2:
        print("Usage: python decode_streams.py input.bin")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    # Read the entire input file into memory
    with open(input_path, "rb") as f:
        rom_data = f.read()

    # For each of the 8 level entries, decode low + high streams
    for idx, level_offset in enumerate(LEVEL_OFFSETS, start=1):
        if level_offset >= len(rom_data):
            print(f"Warning: Level {idx} offset {hex(level_offset)} is beyond file size. Skipping.")
            continue

        # Decode low‐bitplane
        low_decoded, consumed_bytes = decode_low_plane(rom_data, level_offset)

        # Decode high‐bitplane from immediately after the low data
        high_start = consumed_bytes
        high_decoded, _ = decode_high_plane(rom_data, high_start)

        # Write outputs to files
        low_fname = f"stream{idx}low.bin"
        high_fname = f"stream{idx}high.bin"

        with open(low_fname, "wb") as out_low:
            out_low.write(low_decoded)
        with open(high_fname, "wb") as out_high:
            out_high.write(high_decoded)

        print(f"Level {idx:>2}:")
        print(f"  Low  → offset {hex(level_offset)} → {len(low_decoded)} bytes written to '{low_fname}'")
        print(f"  High → offset {hex(high_start)} → {len(high_decoded)} bytes written to '{high_fname}'")

    print("\nDecoding complete.")


if __name__ == "__main__":
    main()
