import os
import re
from collections import defaultdict
import argparse
from PIL import Image, ImageFilter
import sys
import shutil
import subprocess
import logging
import tempfile
import zipfile
import platform

#set up logging
logger = logging.getLogger("MangaPDFConverter")

OUTPUT_DIR_NAME = "PDF"


def get_all_retrace_folders(root):
    """
    finds all folders starting with 'v', 'vol', or 'volume' followed by a number,
    and groups them by standardized volume name (e.g., 'v1', 'v2', etc.).
    """
    logger.debug(f"searching for volume folders in: {root}")

    #regular expression to match folder names like 'v1', 'vol. 2', 'volume 3', etc.
    # captures the prefix (v, vol, or volume) and the volume number
    retrace_pattern = re.compile(r'^(v|vol|volume)\.?\s*(\d+)', re.IGNORECASE)

    #dictionary to store matched folders grouped by standardized volume names (e.g., 'v1')
    volumes = defaultdict(list)

    try:
        #loop through all items in the provided root directory
        for folder in sorted(os.listdir(root)):
            full_path = os.path.join(root, folder)

            #ensure we're only working with directories
            if os.path.isdir(full_path):
                #check if the folder name matches the retrace pattern
                match = retrace_pattern.match(folder)
                if match:
                    #extract the numeric part of the volume (e.g., '2' from 'vol. 2')
                    volume_number = match.group(2)

                    #create a standardized volume key (e.g., always 'v2')
                    volume_name = f"v{volume_number}"

                    #add the folder path to the list associated with this volume key
                    volumes[volume_name].append(full_path)
                    logger.debug(f"found volume folder: {folder} -> {volume_name}")
                else:
                    logger.debug(f"folder {folder} does not match volume pattern")
    except OSError as e:
        logger.error(f"error accessing directory {root}: {e}")
        return defaultdict(list)

    logger.info(
        f"found {len(volumes)} volume groups with {sum(len(folders) for folders in volumes.values())} total folders")
    #return the grouped dictionary of volume folders
    return volumes


def get_all_chapter_folders(root):
    """
    gets all subdirectories in the root folder for chapter mode
    Returns a list of (folder_name, folder_path) tuples
    """
    logger.debug(f"getting all chapter folders from: {root}")
    chapters = []

    try:
        #loop through all items in the root directory
        for folder in sorted(os.listdir(root)):
            #create the full path to the folder
            full_path = os.path.join(root, folder)

            #check if it's actually a directory (not a file)
            if os.path.isdir(full_path):
                chapters.append((folder, full_path))
                logger.debug(f"found chapter folder: {folder}")
    except OSError as e:
        logger.error(f"error accessing directory {root}: {e}")
        return []

    logger.info(f"found {len(chapters)} chapter folders")
    return chapters


def get_hybrid_groups(root):
    """
    groups folders based on whether they belong to a volume or are standalone chapters.
    for folders like "Volume 1 Chapter 1 chapter name", groups all chapters from volume 1 together.
    returns a dict like { "Volume 1": [folder_path1, folder_path2], "standalone_chapter": [folder_path] }
    """
    logger.debug(f"Getting hybrid groups from: {root}")
    hybrid_groups = defaultdict(list)

    #"Volume X Chapter Y" format pattern
    volume_chapter_pattern = re.compile(r'^volume\s+(\d+)\s+chapter\s+\d+', re.IGNORECASE)
    #pattern for simple volume folders (v1, vol1, volume 1)
    simple_volume_pattern = re.compile(r'^(v|vol|volume)\.?\s*(\d+)', re.IGNORECASE)

    try:
        for folder in sorted(os.listdir(root)):
            full_path = os.path.join(root, folder)
            if os.path.isdir(full_path):
                #check for "Volume X Chapter Y" format first
                volume_chapter_match = volume_chapter_pattern.match(folder)
                if volume_chapter_match:
                    volume_number = volume_chapter_match.group(1)
                    volume_key = f"Volume {volume_number}"
                    hybrid_groups[volume_key].append(full_path)
                    logger.debug(f"found volume chapter folder: {folder} -> {volume_key}")
                else:
                    #check for simple volume format (v1, vol1, volume1)
                    simple_volume_match = simple_volume_pattern.match(folder)
                    if simple_volume_match:
                        volume_number = simple_volume_match.group(2)
                        volume_key = f"Volume {volume_number}"
                        hybrid_groups[volume_key].append(full_path)
                        logger.debug(f"found simple volume folder: {folder} -> {volume_key}")
                    else:
                        # standalone chapter or other folder
                        safe_name = re.sub(r'[<>:"/\\|?*]', '_', folder)
                        hybrid_groups[safe_name].append(full_path)
                        logger.debug(f"found standalone chapter: {folder} -> {safe_name}")
    except OSError as e:
        logger.error(f"error accessing directory {root}: {e}")
        return defaultdict(list)

    logger.info(f"created {len(hybrid_groups)} hybrid groups")
    return hybrid_groups


def get_image_files_recursive(folder):
    """
    recursively searches through a folder and finds all image files.
    Returns a sorted list of image file paths.
    """
    logger.debug(f"searching for images recursively in: {folder}")

    #tuple of supported image file extensions
    supported = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
    files = []

    try:
        # os.walk() recursively goes through all subdirectories
        # dirpath = current directory path, filenames = list of files in current directory
        for dirpath, _, filenames in os.walk(folder):
            # Sort filenames to ensure consistent ordering
            for filename in sorted(filenames):
                # Check if file has a supported image extension (case-insensitive)
                if filename.lower().endswith(supported):
                    # Add the full path to our list
                    files.append(os.path.join(dirpath, filename))
    except OSError as e:
        logger.error(f"error walking directory {folder}: {e}")
        return []

    logger.info(f"found {len(files)} image files in {folder}")
    return files


def delete_image_files(image_paths):
    """
    deletes the provided image files and removes empty directories
    """
    logger.info(f"starting deletion of {len(image_paths)} image files")
    deleted_count = 0
    directories_to_check = set()

    for image_path in image_paths:
        try:
            if os.path.exists(image_path):
                #add directory to the set for later cleanup
                directories_to_check.add(os.path.dirname(image_path))
                os.remove(image_path)
                deleted_count += 1
                logger.debug(f"deleted image file: {image_path}")
        except OSError as e:
            logger.warning(f"could not delete {image_path}: {e}")

    #cleanup empty directories
    for directory in directories_to_check:
        try:
            #only remove if directory is empty
            if os.path.exists(directory) and not os.listdir(directory):
                os.rmdir(directory)
                logger.info(f"removed empty directory: {directory}")
        except OSError as e:
            #directory not empty or other error. Skip
            logger.debug(f"could not remove directory {directory}: {e}")

    if deleted_count > 0:
        logger.info(f"successfully deleted {deleted_count} image files")
    else:
        logger.warning("no image files were deleted")


def cleanup_empty_directories_recursive(root_path):
    """
    recursively removes empty directories starting from the deepest level.
    returns True if the root directory was also removed (completely empty).
    """
    logger.debug(f"cleaning up empty directories starting from: {root_path}")

    if not os.path.exists(root_path) or not os.path.isdir(root_path):
        logger.debug(f"path does not exist or is not a directory: {root_path}")
        return False

    removed_root = False

    #first, recursively clean up subdirectories
    try:
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path):
                cleanup_empty_directories_recursive(item_path)
    except OSError as e:
        #directory might have been deleted or inaccessible
        logger.debug(f"error listing directory {root_path}: {e}")

    #then try to remove the current directory if it's empty
    try:
        if os.path.exists(root_path) and not os.listdir(root_path):
            os.rmdir(root_path)
            logger.info(f"removed empty directory: {root_path}")
            removed_root = True
    except OSError as e:
        #directory not empty or other error
        logger.debug(f"could not remove directory {root_path}: {e}")

    return removed_root


def convert_images_to_pdf(image_paths, output_pdf_path, delete_originals=False, settings=None):
    logger.info(f"starting PDF conversion: {len(image_paths)} images -> {output_pdf_path}")

    settings = settings or {}
    image_processing = settings.get("image_processing", "keep_original")
    resize_enabled = settings.get("resize_images", False)
    max_width = settings.get("max_width", 1920)
    max_height = settings.get("max_height", 1080)
    quality = settings.get("pdf_quality", 85)
    auto_open = settings.get("auto_open_pdf", False)
    backup = settings.get("backup_originals", False)
    delete_after = settings.get("delete_after_conversion", False)

    logger.debug(f"PDF conversion settings: processing={image_processing}, resize={resize_enabled}, quality={quality}")

    images = []
    processed_count = 0

    for img_path in image_paths:
        try:
            logger.debug(f"processing image: {img_path}")
            img = Image.open(img_path).convert("RGB")

            #resize if enabled
            if resize_enabled:
                original_size = img.size
                img.thumbnail((max_width, max_height), Image.ANTIALIAS)
                logger.debug(f"resized image from {original_size} to {img.size}")

            #convert format if needed
            if image_processing == "jpeg":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    img.save(temp_file.name, "JPEG", quality=quality)
                    img = Image.open(temp_file.name).convert("RGB")
                    logger.debug(f"Converted image to JPEG format")

            elif image_processing == "png":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    img.save(temp_file.name, "PNG")
                    img = Image.open(temp_file.name).convert("RGB")
                    logger.debug(f"converted image to PNG format")

            images.append(img)
            processed_count += 1

        except Exception as e:
            logger.error(f"failed to process image {img_path}: {e}")

    if not images:
        error_msg = "no valid images to convert"
        logger.error(error_msg)
        raise Exception(error_msg)

    logger.info(f"successfully processed {processed_count}/{len(image_paths)} images")

    #save to PDF
    try:
        logger.debug(f"saving PDF to: {output_pdf_path}")
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
        logger.info(f"successfully created PDF: {output_pdf_path}")
    except Exception as e:
        error_msg = f"failed to save PDF: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)

    #backup originals
    if backup and delete_originals:
        zip_path = output_pdf_path.replace(".pdf", "_backup.zip")
        logger.info(f"creating backup of original images: {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for path in image_paths:
                    if os.path.exists(path):
                        zipf.write(path, os.path.basename(path))
            logger.info(f"successfully created backup: {zip_path}")
        except Exception as e:
            logger.warning(f"could not backup originals: {e}")

    #delete originals
    if delete_originals or delete_after:
        logger.info("deleting original image files")
        deleted_count = 0
        for path in image_paths:
            try:
                os.remove(path)
                deleted_count += 1
                logger.debug(f"deleted original image: {path}")
            except Exception as e:
                logger.warning(f"could not delete image {path}: {e}")
        logger.info(f"deleted {deleted_count}/{len(image_paths)} original images")

    #open the PDF if requested
    if auto_open:
        logger.info(f"attempting to open PDF: {output_pdf_path}")
        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", output_pdf_path])
            elif platform.system() == "Windows":
                os.startfile(output_pdf_path)
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", output_pdf_path])
            logger.info("successfully opened PDF")
        except Exception as e:
            logger.warning(f"could not open PDF: {e}")


def process_folder_groups(folder_groups, output_dir, delete_images=False, settings=None):
    """
    generic function to process grouped folders into PDFs
    folder_groups: dict like {"group_name": [folder_paths]}
    """
    logger.info(f"processing {len(folder_groups)} folder groups")

    for group_name, folders in sorted(folder_groups.items()):
        logger.info(f"processing group: {group_name} ({len(folders)} folder{'s' if len(folders) > 1 else ''})")

        all_images = []
        for folder in sorted(folders):
            logger.debug(f"getting images from folder: {folder}")
            images = get_image_files_recursive(folder)
            all_images.extend(images)

        if not all_images:
            logger.warning(f"no images found in group {group_name}")
            continue

        logger.info(f"found {len(all_images)} total images for group {group_name}")

        #clean group name for filename
        safe_group_name = re.sub(r'[<>:"/\\|?*]', '_', group_name)
        output_pdf = os.path.join(output_dir, f"{safe_group_name}.pdf")

        try:
            convert_images_to_pdf(all_images, output_pdf, delete_images, settings)
            logger.info(f"successfully created PDF for group {group_name}")
        except Exception as e:
            logger.error(f"failed to create PDF for group {group_name}: {e}")


def cleanup_after_processing(root, delete_images):
    """
    helper function to handle cleanup after processing
    """
    logger.info("starting post-processing cleanup")
    root_was_removed = cleanup_empty_directories_recursive(root)
    if root_was_removed:
        logger.info(f"removed empty manga directory: {root}")
    elif delete_images:
        logger.warning(f"could not remove manga directory (may not be empty): {root}")


def process_volumes(root, delete_images=False, settings=None):
    """process images by grouping them into volumes"""
    logger.info("starting volume processing mode")
    volume_folders = get_all_retrace_folders(root)

    if not volume_folders:
        logger.warning("no volume folders found (folders starting with 'v' followed by numbers)")
        return

    manga_name = os.path.basename(os.path.abspath(root))
    output_base = settings.get('output_folder') if settings else None
    output_base = output_base or os.path.dirname(root)
    output_dir = os.path.join(output_base, OUTPUT_DIR_NAME, manga_name)

    logger.info(f"creating output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    logger.info("processing in VOLUMES mode (grouping by volume name)")
    process_folder_groups(volume_folders, output_dir, delete_images, settings)

    #always clean up empty directories after processing
    cleanup_after_processing(root, delete_images)
    logger.info("Volume processing completed")


def process_chapters(root, delete_images=False, settings=None):
    """process images by converting each folder into its own PDF"""
    logger.info("starting chapter processing mode")
    chapter_folders = get_all_chapter_folders(root)

    if not chapter_folders:
        logger.warning("no folders found in the specified directory")
        return

    logger.info(f"found {len(chapter_folders)} folders to process")

    #convert to the same format as other grouping functions
    chapter_groups = {folder_name: [folder_path] for folder_name, folder_path in chapter_folders}

    manga_name = os.path.basename(os.path.abspath(root))
    output_base = settings.get('output_folder') if settings else None
    output_base = output_base or os.path.dirname(root)
    output_dir = os.path.join(output_base, OUTPUT_DIR_NAME, manga_name)

    logger.info(f"creating output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    logger.info("processing in CHAPTERS mode (each folder becomes a PDF)")
    process_folder_groups(chapter_groups, output_dir, delete_images, settings)

    #always clean up empty directories after processing
    cleanup_after_processing(root, delete_images)
    logger.info("chapter processing completed")


def process_hybrid(root, delete_images=False, settings=None):
    """process images using hybrid grouping (volumes + individual chapters)"""
    logger.info("starting hybrid processing mode")
    hybrid_groups = get_hybrid_groups(root)

    if not hybrid_groups:
        logger.warning("no folders found for hybrid processing")
        return

    manga_name = os.path.basename(os.path.abspath(root))
    output_base = settings.get('output_folder') if settings else None
    output_base = output_base or os.path.dirname(root)
    output_dir = os.path.join(output_base, OUTPUT_DIR_NAME, manga_name)

    logger.info(f"creating output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    logger.info("processing in HYBRID mode (grouping volumes and individual chapters)")
    process_folder_groups(hybrid_groups, output_dir, delete_images, settings)

    #always clean up empty directories after processing
    cleanup_after_processing(root, delete_images)
    logger.info("hybrid processing completed")


def main():
    """
    main function that handles command-line arguments and orchestrates the conversion process.
    """
    #set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="convert manga images to PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\nexamples:
  # convert by volumes (groups folders like v1, v1.1, v1.2 into v1.pdf)
  python3 images_to_volumes.py /path/to/manga --mode volumes

  # Convert each folder to its own PDF
  python3 images_to_volumes.py /path/to/manga --mode chapters

  # Use hybrid mode (mix of volumes and individual chapters)
  python3 images_to_volumes.py /path/to/manga --mode hybrid
        """
    )

    parser.add_argument(
        'path',
        help='path to the folder containing manga images'
    )

    parser.add_argument(
        '--mode',
        choices=['volumes', 'chapters', 'hybrid'],
        default='hybrid',
        help='processing mode: "volumes" groups folders by volume name, "chapters" converts each folder separately, "hybrid" mixes both (default: hybrid)'
    )

    parser.add_argument(
        '--delete-images',
        action='store_true',
        help='delete source images after successful PDF conversion (also removes empty directories)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='enable debug logging'
    )

    #parse command-line arguments
    args = parser.parse_args()

    #set up logging based on debug flag
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info("=== MangaPDFConverter Started ===")
    logger.info(f"processing path: {args.path}")
    logger.info(f"mode: {args.mode}")
    logger.info(f"delete images: {args.delete_images}")
    logger.info(f"debug mode: {args.debug}")

    #check if the provided path is actually a directory
    if not os.path.isdir(args.path):
        logger.error(f"'{args.path}' is not a valid folder")
        sys.exit(1)

    #warn user if they are about to delete images
    if args.delete_images:
        logger.warning("image files and empty directories will be deleted after conversion!")
        print("WARNING: image files and empty directories will be deleted after conversion!")
        response = input("are you sure you want to continue (Y/N)? ")
        if response.lower() not in ['y', 'yes']:
            logger.info("operation cancelled by user")
            sys.exit(0)

    try:
        #process based on selected mode
        if args.mode == 'volumes':
            process_volumes(args.path, args.delete_images)
        elif args.mode == 'chapters':
            process_chapters(args.path, args.delete_images)
        else:
            process_hybrid(args.path, args.delete_images)

        logger.info("=== MangaPDFConverter completed successfully ===")

    except Exception as e:
        logger.error(f"Fatal error during processing: {e}")
        sys.exit(1)


#this runs only when the script is executed directly
if __name__ == "__main__":
    main()