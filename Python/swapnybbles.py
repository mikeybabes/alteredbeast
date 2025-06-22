import sys

def swap_nibble(byte):
    return ((byte & 0x0F) << 4 | (byte & 0xF0) >> 4)

def process_file(input_file):
    with open(input_file, 'rb') as f:
        data = f.read()

    swapped_data = bytes(swap_nibble(byte) for byte in data)

    output_file = 'swapped_' + input_file
    with open(output_file, 'wb') as f:
        f.write(swapped_data)

    print(f"Processed file saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python swapnibble.py input.bin")
        sys.exit(1)

    input_file = sys.argv[1]
    process_file(input_file)
