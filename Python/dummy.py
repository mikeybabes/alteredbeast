import sys

def create_hex_file(filename, size, fill_value):
    try:
        size = int(size, 16)
        fill_value = int(fill_value, 16)

        with open(filename, 'wb') as f:
            f.write(bytearray([fill_value] * size))

        print(f"File '{filename}' created with size {size} bytes, filled with 0x{fill_value:02X}.")
    except ValueError as e:
        print(f"Error: {e}. Ensure the size and fill value are valid hex numbers.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python dummy.py <filename> <size> <fill_value>")
    else:
        _, filename, size, fill_value = sys.argv
        create_hex_file(filename, size, fill_value)
