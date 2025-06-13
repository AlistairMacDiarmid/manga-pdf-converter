import os
import re
from collections import defaultdict

import argparse
from PIL import Image
import sys

OUTPUT_DIR_NAME = "PDF"


def get_all_retrace_folders(root):
    """
    Finds all folders starting with 'v', 'vol', or 'volume' followed by a number,
    and groups them by standardized volume name (e.g., 'v1', 'v2', etc.).
    """

    # Regular expression to match folder names like 'v1', 'vol. 2', 'volume 3', etc.
    # Captures the prefix (v, vol, or volume) and the volume number
    retrace_pattern = re.compile(r'^(v|vol|volume)\.?\s*(\d+)', re.IGNORECASE)

    # Dictionary to store matched folders grouped by standardized volume names (e.g., 'v1')
    volumes = defaultdict(list)

    # Loop through all items in the provided root directory
    for folder in sorted(os.listdir(root)):
        full_path = os.path.join(root, folder)

        # Ensure we're only working with directories
        if os.path.isdir(full_path):
            # Check if the folder name matches the retrace pattern
            match = retrace_pattern.match(folder)
            if match:
                # Extract the numeric part of the volume (e.g., '2' from 'vol. 2')
                volume_number = match.group(2)

                # Create a standardized volume key (e.g., always 'v2')
                volume_name = f"v{volume_number}"

                # Add the folder path to the list associated with this volume key
                volumes[volume_name].append(full_path)

    # Return the grouped dictionary of volume folders
    return volumes

def get_all_chapter_folders(root):
    """
    Gets all subdirectories in the root folder for chapter mode
    Returns a list of (folder_name, folder_path) tuples
    """
    chapters = []

    #Loop through all items in the root directory
    for folder in sorted(os.listdir(root)):
        #Create the full path to the folder
        full_path = os.path.join(root, folder)

        #check if it's actually a directory (not a file)
        if os.path.isdir(full_path):
            chapters.append((folder, full_path))

    return chapters

def get_hybrid_groups(root):
    """
    Groups folders based on whether they belong to a volume or are standalone chapters.
    Returns a dict like { "Vol.6": [folder_path1, folder_path2], "50.": [folder_path3] }
    """
    hybrid_groups = defaultdict(list)
    volume_pattern = re.compile(r'^(Vol\.?\s*\d+)', re.IGNORECASE)

    for folder in sorted(os.listdir(root)):
        full_path = os.path.join(root, folder)
        if os.path.isdir(full_path):
            match = volume_pattern.match(folder)
            if match:
                volume = match.group(1).replace(" ", "").replace("Vol.", "Vol")
                hybrid_groups[volume].append(full_path)
            else:
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', folder)
                hybrid_groups[safe_name].append(full_path)
    return hybrid_groups


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


def process_volumes(root):
    """
    Process images by grouping them into volumes
    """
    #Get all volume folders organised by volume name
    volume_folders = get_all_retrace_folders(root)

    if not volume_folders:
        print("No volume folders found (folders starting with 'v' followed by numbers)")
        return

    manga_name = os.path.basename(os.path.abspath(root))
    output_dir = os.path.join(os.path.dirname(root), OUTPUT_DIR_NAME, manga_name)
    os.makedirs(output_dir, exist_ok=True)

    #Process each volume
    for volume, folders in sorted(volume_folders.items()):
        print(f"\nProcessing {volume} ({len(folders)} retraces)")

        #Collect all images from all folders belonging to this volume
        all_images = []
        for folder in sorted(folders):
            images = get_image_files_recursive(folder)
            all_images.extend(images)


        #Create output PDF filename (e.g., "v1.pdf", "v2.pdf")
        output_pdf = os.path.join(output_dir, f"{volume}.pdf")

        #convert all images for this volume into a single PDF
        convert_images_to_pdf(all_images, output_pdf)


def process_chapters(root):
    """
    Process images by converting each folder into its own PDF
    """
    #Get all chapter folders
    chapter_folders = get_all_chapter_folders(root)

    if not chapter_folders:
        print("No folders found in the specified directory")
        return

    print(f"Found {len(chapter_folders)} folders to process")

    manga_name = os.path.basename(os.path.abspath(root))
    output_dir = os.path.join(os.path.dirname(root), OUTPUT_DIR_NAME, manga_name)
    os.makedirs(output_dir, exist_ok=True)

    #Process each chapter folder
    for folder_name, folder_path in chapter_folders:
        print(f"\nProcessing folder: {folder_name}")

        #Get all images in this folder
        images = get_image_files_recursive(folder_path)

        if not images:
            print(f"No images found in {folder_name}")
            continue

        #Create output PDF filename based on folder name
        #Replace any characters that might be problematic in filenames
        safe_folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)
        output_pdf = os.path.join(output_dir, f"{safe_folder_name}.pdf")

        #Convert images to PDF
        convert_images_to_pdf(images, output_pdf)


def process_hybrid(root):
    hybrid_groups = get_hybrid_groups(root)

    if not hybrid_groups:
        print("No folders found for hybrid processing")
        return

    manga_name = os.path.basename(os.path.abspath(root))
    output_dir = os.path.join(os.path.dirname(root), OUTPUT_DIR_NAME, manga_name)
    os.makedirs(output_dir, exist_ok=True)

    for group_name, folders in sorted(hybrid_groups.items()):
        print(f"\nProcessing {group_name} ({len(folders)} folders)")
        all_images = []
        for folder in folders:
            images = get_image_files_recursive(folder)
            all_images.extend(images)

        if not all_images:
            print(f"No images found in {group_name}")
            continue

        output_pdf = os.path.join(output_dir, f"{group_name}.pdf")
        convert_images_to_pdf(all_images, output_pdf)


def main():
    """
    Main function that handles command-line arguments and orchestrates the conversion process.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Convert manga images to PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\nExamples:\n  # Convert by volumes (groups folders like v1, v1.1, v1.2 into v1.pdf)\n  python3 images_to_volumes.py /path/to/manga --mode volumes\n\n  # Convert each folder to its own PDF\n  python3 images_to_volumes.py /path/to/manga --mode chapters\n        """
    )

    parser.add_argument(
        'path',
        help='Path to the folder containing manga images'
    )

    parser.add_argument(
        '--mode',
        choices=['volumes', 'chapters', 'hybrid'],
        default='volumes',
        help='Processing mode: "volumes" groups folders by volume name, "chapters" converts each folder separately, "hybrid" mixes both (default: volumes)'
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Check if the provided path is actually a directory
    if not os.path.isdir(args.path):
        print(f"'{args.path}' is not a valid folder.")
        sys.exit(1)

    # Process based on selected mode
    if args.mode == 'volumes':
        print("Processing in VOLUMES mode (grouping by volume name)")
        process_volumes(args.path)
    elif args.mode == 'hybrid':
        print("Processing in HYBRID mode (grouping volumes and individual chapters)")
        process_hybrid(args.path)
    else:
        print("Processing in CHAPTERS mode (each folder becomes a PDF)")
        process_chapters(args.path)


# This runs only when the script is executed directly
if __name__ == "__main__":
    main()