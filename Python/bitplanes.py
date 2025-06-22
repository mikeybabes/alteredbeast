import sys

def combine_bitplanes(plane1_file, plane2_file, plane3_file, output_file):
    # Open the input bitplane files in binary read mode
    with open(plane1_file, 'rb') as plane1, open(plane2_file, 'rb') as plane2, open(plane3_file, 'rb') as plane3:
        # Read the bitplane data
        plane1_data = plane1.read()
        plane2_data = plane2.read()
        plane3_data = plane3.read()

        # Ensure all bitplanes have the same size
        if not (len(plane1_data) == len(plane2_data) == len(plane3_data)):
            print("Error: Input files must be of the same size.")
            return
        
        # The output file will be 4 times the size of the input files
        combined_data = bytearray(len(plane1_data) * 4)

        # Combine the bitplanes
        for byte_index in range(len(plane1_data)):
            for bit_pair in range(4):
                shift = 7 - (bit_pair * 2)
                bit1_pixel1 = (plane1_data[byte_index] >> shift) & 0x01
                bit2_pixel1 = (plane2_data[byte_index] >> shift) & 0x01
                bit3_pixel1 = (plane3_data[byte_index] >> shift) & 0x01

                shift = 7 - (bit_pair * 2 + 1)
                bit1_pixel2 = (plane1_data[byte_index] >> shift) & 0x01
                bit2_pixel2 = (plane2_data[byte_index] >> shift) & 0x01
                bit3_pixel2 = (plane3_data[byte_index] >> shift) & 0x01

                pixel1 = (bit1_pixel1 << 2) | (bit2_pixel1 << 1) | bit3_pixel1
                pixel2 = (bit1_pixel2 << 2) | (bit2_pixel2 << 1) | bit3_pixel2

                combined_byte_index = byte_index * 4 + bit_pair

                combined_data[combined_byte_index] = (pixel1 << 4) | pixel2  # Set the combined byte

    # Write the combined data to the output file in binary write mode
    with open(output_file, 'wb') as output:
        output.write(combined_data)

    print(f"Combined bitplane file saved as {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python bitplanes.py plane1.bin plane2.bin plane3.bin finalplane.bin")
    else:
        plane1_file = sys.argv[1]
        plane2_file = sys.argv[2]
        plane3_file = sys.argv[3]
        output_file = sys.argv[4]
        combine_bitplanes(plane1_file, plane2_file, plane3_file, output_file)


