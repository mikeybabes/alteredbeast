import sys
from PIL import Image

def combine_images_side_by_side(image_paths, output_path):
    """
    Combine multiple PNG images side by side
    - image_paths: List of input image paths
    - output_path: Output filename
    """
    try:
        # Open all images
        images = [Image.open(img) for img in image_paths]
        
        # Verify all images have same height
        heights = {img.height for img in images}
        if len(heights) > 1:
            raise ValueError(f"Images have different heights: {heights}")
        
        # Calculate total width
        total_width = sum(img.width for img in images)
        max_height = images[0].height
        
        # Create new image
        combined = Image.new('RGBA', (total_width, max_height))
        
        # Paste images side by side
        x_offset = 0
        for img in images:
            combined.paste(img, (x_offset, 0))
            x_offset += img.width
        
        # Save result
        combined.save(output_path)
        print(f"Successfully combined {len(image_paths)} images:")
        for path in image_paths:
            print(f"- {path} ({Image.open(path).width}x{Image.open(path).height})")
        print(f"Output: {output_path} ({total_width}x{max_height})")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Usage: python combine.py img1.png img2.png output.png")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python combine.py img1.png img2.png [...] output.png")
        print("Example: python combine.py title1.png title2.png combined.png")
        sys.exit(1)
    
    # All args except last are input images
    input_files = sys.argv[1:-1]
    output_file = sys.argv[-1]
    
    combine_images_side_by_side(input_files, output_file)