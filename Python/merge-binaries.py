import sys

def merge_binaries(file1_path, file2_path, output_path, byte_amount):
    with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2, open(output_path, 'wb') as output:
        while True:
            chunk1 = file1.read(byte_amount)
            chunk2 = file2.read(byte_amount)
            if not chunk1 or not chunk2:
                break
            output.write(chunk1 + chunk2)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python merge_binaries.py <input1.bin> <input2.bin> <output.bin> <byte_amount>")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    output_path = sys.argv[3]
    byte_amount = int(sys.argv[4])

    merge_binaries(file1_path, file2_path, output_path, byte_amount)

