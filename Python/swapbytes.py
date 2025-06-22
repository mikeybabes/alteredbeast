import sys

def swap_bytes(file_path, count):
    try:
        with open(file_path, 'rb') as file:
            data = bytearray(file.read())
        
        # Ensure file length is divisible by count * 2
        if len(data) % (count * 2) != 0:
            print("File length is not a multiple of", count * 2)
            return

        # Perform the swapping
        for i in range(0, len(data), count * 2):
            for j in range(count):
                # Swap bytes
                data[i + j], data[i + count + j] = data[i + count + j], data[i + j]

        # Write the modified data back to the file
        with open(file_path, 'wb') as file:
            file.write(data)

        print("Swapping completed successfully.")

    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python swapbytes.py <file_path> <count>")
    else:
        file_path = sys.argv[1]
        count = int(sys.argv[2])
        swap_bytes(file_path, count)
