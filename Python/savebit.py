import sys

def savebit(input_filename, output_filename, hex_offset, hex_length):
    # Convert hex offset and length to integers
    offset = int(hex_offset, 16)
    length = int(hex_length, 16)
    end_address = offset + length - 1
    
    try:
        # Open the input file in binary mode and read the specified portion
        with open(input_filename, 'rb') as infile:
            infile.seek(offset)
            data = infile.read(length)
        
        # Write the read data to the output file
        with open(output_filename, 'wb') as outfile:
            outfile.write(data)
        
        print(f"Successfully saved {length} bytes from {input_filename} (offset {hex_offset}) to {output_filename}")
        print(f"Data saved from offset {hex(offset)} to {hex(end_address)}")
    
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: savebit.py <input_filename> <output_filename> <hex_offset> <hex_length>")
    else:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
        hex_offset = sys.argv[3]
        hex_length = sys.argv[4]
        savebit(input_filename, output_filename, hex_offset, hex_length)
