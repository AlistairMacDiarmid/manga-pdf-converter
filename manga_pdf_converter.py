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

    # Loop through all items in the root directory
    for folder in sorted(os.listdir(root)):
        # Create the full path to the folder
        full_path = os.path.join(root, folder)

        # check if it's actually a directory (not a file)
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


def delete_image_files(image_paths):
    """
    Deletes the provided image files and removes empty directories
    """
    deleted_count = 0
    directories_to_check = set()

    for image_path in image_paths:
        try:
            if os.path.exists(image_path):
                # Add directory to the set for later cleanup
                directories_to_check.add(os.path.dirname(image_path))
                os.remove(image_path)
                deleted_count += 1
        except OSError as e:
            print(f"Warning: could not delete {image_path}: {e}")

    # Cleanup empty directories
    for directory in directories_to_check:
        try:
            # Only remove if directory is empty
            if os.path.exists(directory) and not os.listdir(directory):
                os.rmdir(directory)
                print(f"Removed empty directory {directory}")
        except OSError:
            # Directory not empty or other error. Skip
            pass

    if deleted_count > 0:
        print(f"Deleted {deleted_count} image files")


def cleanup_empty_directories_recursive(root_path):
    """
    Recursively removes empty directories starting from the deepest level.
    Returns True if the root directory was also removed (completely empty).
    """
    if not os.path.exists(root_path) or not os.path.isdir(root_path):
        return False

    removed_root = False

    # First, recursively clean up subdirectories
    try:
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path):
                cleanup_empty_directories_recursive(item_path)
    except OSError:
        # Directory might have been deleted or inaccessible
        pass

    # Then try to remove the current directory if it's empty
    try:
        if os.path.exists(root_path) and not os.listdir(root_path):
            os.rmdir(root_path)
            print(f"Removed empty directory: {root_path}")
            removed_root = True
    except OSError:
        # Directory not empty or other error
        pass

    return removed_root


def convert_images_to_pdf(image_paths, output_path, delete_images=False):
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

    try:
        # Save the first image as PDF, with all other images appended
        first.save(output_path, save_all=True, append_images=rest)

        # Print success message with page count
        print(f"Saved {output_path} ({len(image_paths)} pages)")

        # Delete source images if requested and conversion was successful
        if delete_images:
            delete_image_files(image_paths)
    except Exception as e:
        print(f"Failed to save PDF {output_path}: {e}")
        return
    finally:
        # Clean up memory by closing all images
        first.close()
        for img in rest:
            img.close()


def process_folder_groups(folder_groups, output_dir, delete_images=False):
    """
    Generic function to process grouped folders into PDFs
    folder_groups: dict like {"group_name": [folder_paths]}
    """
    for group_name, folders in sorted(folder_groups.items()):
        print(f"\nProcessing {group_name} ({len(folders)} folder{'s' if len(folders) > 1 else ''})")

        all_images = []
        for folder in sorted(folders):
            images = get_image_files_recursive(folder)
            all_images.extend(images)

        if not all_images:
            print(f"No images found in {group_name}")
            continue

        # Clean group name for filename
        safe_group_name = re.sub(r'[<>:"/\\|?*]', '_', group_name)
        output_pdf = os.path.join(output_dir, f"{safe_group_name}.pdf")
        convert_images_to_pdf(all_images, output_pdf, delete_images)


def cleanup_after_processing(root, delete_images):
    """
    Helper function to handle cleanup after processing
    """
    root_was_removed = cleanup_empty_directories_recursive(root)
    if root_was_removed:
        print(f"Removed empty manga directory: {root}")
    elif delete_images:
        print(f"Warning: Could not remove manga directory (may not be empty): {root}")


def process_volumes(root, delete_images=False):
    """Process images by grouping them into volumes"""
    volume_folders = get_all_retrace_folders(root)

    if not volume_folders:
        print("No volume folders found (folders starting with 'v' followed by numbers)")
        return

    manga_name = os.path.basename(os.path.abspath(root))
    output_dir = os.path.join(os.path.dirname(root), OUTPUT_DIR_NAME, manga_name)
    os.makedirs(output_dir, exist_ok=True)

    print("Processing in VOLUMES mode (grouping by volume name)")
    process_folder_groups(volume_folders, output_dir, delete_images)

    # Always clean up empty directories after processing
    cleanup_after_processing(root, delete_images)


def process_chapters(root, delete_images=False):
    """Process images by converting each folder into its own PDF"""
    chapter_folders = get_all_chapter_folders(root)

    if not chapter_folders:
        print("No folders found in the specified directory")
        return

    print(f"Found {len(chapter_folders)} folders to process")

    # Convert to the same format as other grouping functions
    chapter_groups = {folder_name: [folder_path] for folder_name, folder_path in chapter_folders}

    manga_name = os.path.basename(os.path.abspath(root))
    output_dir = os.path.join(os.path.dirname(root), OUTPUT_DIR_NAME, manga_name)
    os.makedirs(output_dir, exist_ok=True)

    print("Processing in CHAPTERS mode (each folder becomes a PDF)")
    process_folder_groups(chapter_groups, output_dir, delete_images)

    # Always clean up empty directories after processing
    cleanup_after_processing(root, delete_images)


def process_hybrid(root, delete_images=False):
    """Process images using hybrid grouping (volumes + individual chapters)"""
    hybrid_groups = get_hybrid_groups(root)

    if not hybrid_groups:
        print("No folders found for hybrid processing")
        return

    manga_name = os.path.basename(os.path.abspath(root))
    output_dir = os.path.join(os.path.dirname(root), OUTPUT_DIR_NAME, manga_name)
    os.makedirs(output_dir, exist_ok=True)

    print("Processing in HYBRID mode (grouping volumes and individual chapters)")
    process_folder_groups(hybrid_groups, output_dir, delete_images)

    # Always clean up empty directories after processing
    cleanup_after_processing(root, delete_images)


def main():
    """
    Main function that handles command-line arguments and orchestrates the conversion process.
    """
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Convert manga images to PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\nExamples:
  # Convert by volumes (groups folders like v1, v1.1, v1.2 into v1.pdf)
  python3 images_to_volumes.py /path/to/manga --mode volumes

  # Convert each folder to its own PDF
  python3 images_to_volumes.py /path/to/manga --mode chapters

  # Use hybrid mode (mix of volumes and individual chapters)
  python3 images_to_volumes.py /path/to/manga --mode hybrid
        """
    )

    parser.add_argument(
        'path',
        help='Path to the folder containing manga images'
    )

    parser.add_argument(
        '--mode',
        choices=['volumes', 'chapters', 'hybrid'],
        default='hybrid',
        help='Processing mode: "volumes" groups folders by volume name, "chapters" converts each folder separately, "hybrid" mixes both (default: hybrid)'
    )

    parser.add_argument(
        '--delete-images',
        action='store_true',
        help='Delete source images after successful PDF conversion (also removes empty directories)'
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Check if the provided path is actually a directory
    if not os.path.isdir(args.path):
        print(f"'{args.path}' is not a valid folder.")
        sys.exit(1)

    # Warn user if they are about to delete images
    if args.delete_images:
        print("WARNING: Image files and empty directories will be deleted after conversion!")
        response = input("Are you sure you want to continue (Y/N)? ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled")
            sys.exit(0)

    # Process based on selected mode
    if args.mode == 'volumes':
        process_volumes(args.path, args.delete_images)
    elif args.mode == 'chapters':
        process_chapters(args.path, args.delete_images)
    else:
        process_hybrid(args.path, args.delete_images)


# This runs only when the script is executed directly
if __name__ == "__main__":
    main()