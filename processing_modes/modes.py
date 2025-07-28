import os
import logging
import re

from utils.getters import get_all_retrace_folders, get_all_chapter_folders, get_hybrid_groups
from utils.cleanup import cleanup_empty_directories_recursive
from pdf_conversion.converter import process_folder_groups

OUTPUT_DIR_NAME = "PDF"
logger = logging.getLogger("MangaPDFConverter")


class MangaProcessingError(Exception):
    """custom exception for manga processing errors."""
    pass


def cleanup_after_processing(root, delete_images):
    """
    perform cleanup by removing empty directories after processing.

    Args:
        root (str): Root directory path to clean up.
        delete_images (bool): Whether images were deleted, used for logging context.
    """
    logger.info("starting post-processing cleanup")
    root_was_removed = cleanup_empty_directories_recursive(root)
    if root_was_removed:
        logger.info(f"removed empty manga directory: {root}")
    elif delete_images:
        logger.warning(f"could not remove manga directory (may not be empty): {root}")


def process_volumes(root, delete_images=False, settings=None):
    """
    process manga folders grouped by volumes, converting images inside each volume folder to PDFs.

    Args:
        root (str): Root directory containing volume folders.
        delete_images (bool): Whether to delete images after conversion.
        settings (dict): Optional settings controlling processing and output paths.

    Raises:
        MangaProcessingError: If no volume folders are found or processing fails.
    """
    logger.info("starting volume processing mode")

    #check if root directory exists
    if not os.path.exists(root):
        raise MangaProcessingError(f"root directory does not exist: {root}")

    if not os.path.isdir(root):
        raise MangaProcessingError(f"path is not a directory: {root}")

    #get all volume folders, i.e., folders starting with 'v' followed by numbers
    volume_folders = get_all_retrace_folders(root)
    if not volume_folders:
        logger.warning("no volume folders found (folders starting with 'v' followed by numbers)")
        raise MangaProcessingError(
            "no volume folders found in the specified directory. Expected folders named like 'v1', 'vol.2', 'volume 3', etc.")

    #derive manga name and output directory path
    manga_name = os.path.basename(os.path.abspath(root))
    output_base = settings.get('output_folder') if settings else os.path.dirname(root)
    output_dir = os.path.join(output_base, OUTPUT_DIR_NAME, manga_name)

    #create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
    except PermissionError:
        raise MangaProcessingError(f"permission denied creating output directory: {output_dir}")
    except OSError as e:
        raise MangaProcessingError(f"failed to create output directory: {e}")

    logger.info("processing in volumes mode (grouping by volume name)")
    #process the groups and generate PDFs
    try:
        process_folder_groups(volume_folders, output_dir, delete_images, settings)
    except Exception as e:
        raise MangaProcessingError(f"Failed to process volume folders: {e}")

    # cleanup any empty directories after processing
    cleanup_after_processing(root, delete_images)


def process_chapters(root, delete_images=False, settings=None):
    """
    process manga folders where each folder is treated as a single chapter to be converted into its own PDF.

    Args:
        root (str): Root directory containing chapter folders.
        delete_images (bool): Whether to delete images after conversion.
        settings (dict): Optional settings controlling processing and output paths.

    Raises:
        MangaProcessingError: If no chapter folders are found or processing fails.
    """
    logger.info("starting chapter processing mode")

    #check if root directory exists
    if not os.path.exists(root):
        raise MangaProcessingError(f"root directory does not exist: {root}")

    if not os.path.isdir(root):
        raise MangaProcessingError(f"path is not a directory: {root}")

    #get all chapter folders
    chapter_folders = get_all_chapter_folders(root)
    if not chapter_folders:
        logger.warning("no folders found in the specified directory")
        raise MangaProcessingError("no chapter folders found in the specified directory.")

    #convert list of (folder_name, folder_path) tuples to dictionary for processing
    chapter_groups = {folder_name: [folder_path] for folder_name, folder_path in chapter_folders}

    #derive manga name and output directory path
    manga_name = os.path.basename(os.path.abspath(root))
    output_base = settings.get('output_folder') if settings else os.path.dirname(root)
    output_dir = os.path.join(output_base, OUTPUT_DIR_NAME, manga_name)

    #create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
    except PermissionError:
        raise MangaProcessingError(f"permission denied creating output directory: {output_dir}")
    except OSError as e:
        raise MangaProcessingError(f"failed to create output directory: {e}")

    logger.info("processing in chapters mode (each folder becomes a pdf)")
    #process the groups and generate PDFs
    try:
        process_folder_groups(chapter_groups, output_dir, delete_images, settings)
    except Exception as e:
        raise MangaProcessingError(f"failed to process chapter folders: {e}")

    #cleanup any empty directories after processing
    cleanup_after_processing(root, delete_images)


def process_hybrid(root, delete_images=False, settings=None):
    """
    process manga folders using a hybrid approach combining volume and chapter grouping.

    Args:
        root (str): Root directory containing hybrid-structured folders.
        delete_images (bool): Whether to delete images after conversion.
        settings (dict): Optional settings controlling processing and output paths.

    Raises:
        MangaProcessingError: If no folders are found or processing fails.
    """
    logger.info("starting hybrid processing mode")

    #check if root directory exists
    if not os.path.exists(root):
        raise MangaProcessingError(f"root directory does not exist: {root}")

    if not os.path.isdir(root):
        raise MangaProcessingError(f"path is not a directory: {root}")

    #get hybrid groups for processing
    hybrid_groups = get_hybrid_groups(root)
    if not hybrid_groups:
        logger.warning("no folders found for hybrid processing")
        raise MangaProcessingError("No folders found for hybrid processing in the specified directory.")

    #derive manga name and output directory path
    manga_name = os.path.basename(os.path.abspath(root))
    output_base = settings.get('output_folder') if settings else os.path.dirname(root)
    output_dir = os.path.join(output_base, OUTPUT_DIR_NAME, manga_name)

    #create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
    except PermissionError:
        raise MangaProcessingError(f"permission denied creating output directory: {output_dir}")
    except OSError as e:
        raise MangaProcessingError(f"failed to create output directory: {e}")

    logger.info("processing in hybrid mode (grouping volumes and individual chapters)")
    #process the groups and generate PDFs
    try:
        process_folder_groups(hybrid_groups, output_dir, delete_images, settings)
    except Exception as e:
        raise MangaProcessingError(f"failed to process hybrid groups: {e}")

    #cleanup any empty directories after processing
    cleanup_after_processing(root, delete_images)