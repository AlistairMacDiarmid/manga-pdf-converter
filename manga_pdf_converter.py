import os
import re
from collections import defaultdict
from PIL import Image
import sys


def get_all_retrace_folders(root):
    """
    Finds all folders that start with 'v' followed by numbers (like v1, v2, etc.)
    and groups them by volume name.
    """
    # Create a regex pattern to match folders starting with 'v' and digits
    retrace_pattern = re.compile(r'^(v\d+)', re.IGNORECASE)

    # defaultdict creates a dictionary where missing keys automatically get an empty list
    volumes = defaultdict(list)

    # Loop through all items in the root directory
    for folder in sorted(os.listdir(root)):
        # Create the full path to the folder
        full_path = os.path.join(root, folder)

        # Check if it's actually a directory (not a file)
        if os.path.isdir(full_path):
            # Try to match the folder name against defined pattern
            match = retrace_pattern.match(folder)
            if match:
                # Extract the volume name ('v1', 'v2', etc.)
                volume_name = match.group(1)
                # Add this folder path to the list for this volume
                volumes[volume_name].append(full_path)

    return volumes


def get_image_files_recursive(folder):
    """
    Recursively searches through a folder and finds all image files.
    Returns a sorted list of image file paths.
    """
    # Tuple of supported image file extensions
    supported = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
    files = []

    # os.walk() recursively goes through all subdirectories
    # dirpath = current directory path, filenames = list of files in current directory
    for dirpath, _, filenames in os.walk(folder):
        # Sort filenames to ensure consistent ordering
        for filename in sorted(filenames):
            # Check if file has a supported image extension (case-insensitive)
            if filename.lower().endswith(supported):
                # Add the full path to our list
                files.append(os.path.join(dirpath, filename))
    return files


def convert_images_to_pdf(image_paths, output_path):
    """
    Takes a list of image file paths and converts them into a single PDF file.
    """
    # If no images provided, skip conversion
    if not image_paths:
        print(f"No images to convert for {output_path}")
        return

    # Try to open the first image and convert it to RGB format
    try:
        first = Image.open(image_paths[0]).convert("RGB")
    except Exception as e:
        print(f"Failed to open first image: {e}")
        return

    # Process all remaining images
    rest = []
    for path in image_paths[1:]:  # Skip the first image (index 0)
        try:
            # Open image, convert to RGB, and make a copy
            img = Image.open(path).convert("RGB")
            rest.append(img.copy())
            img.close()  # Close the original to free memory
        except Exception as e:
            # If an image fails to open, skip it but continue with others
            print(f"Skipping image {path}: {e}")

    # Save the first image as PDF, with all other images appended
    first.save(output_path, save_all=True, append_images=rest)

    # Clean up memory by closing all images
    first.close()
    for img in rest:
        img.close()

    # Print success message with page count
    print(f"Saved {output_path} ({len(image_paths)} pages)")


def main(root):
    """
    Main function that orchestrates the entire conversion process.
    """
    # Check if the provided path is actually a directory
    if not os.path.isdir(root):
        print(f"'{root}' is not a valid folder.")
        return

    # Get all volume folders organised by volume name
    volume_folders = get_all_retrace_folders(root)

    # Process each volume
    for volume, folders in sorted(volume_folders.items()):
        print(f"\nProcessing {volume} ({len(folders)} retraces)")

        # Collect all images from all folders belonging to this volume
        all_images = []
        for folder in sorted(folders):
            images = get_image_files_recursive(folder)
            all_images.extend(images)  # Add all images to our main list

        # Create output PDF filename (e.g., "v1.pdf", "v2.pdf")
        output_pdf = f"{volume}.pdf"

        # Convert all images for this volume into a single PDF
        convert_images_to_pdf(all_images, output_pdf)


# This runs only when the script is executed directly
if __name__ == "__main__":
    # Check if user provided exactly one command line argument
    if len(sys.argv) != 2:
        print("Usage: python3 images_to_volumes.py <path_to_top_level_manga_folder>")
        sys.exit(1)  # Exit with error code

    # Run the main function with the provided folder path
    main(sys.argv[1])  # sys.argv[1] is the first command line argument