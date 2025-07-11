import os
import logging

logger = logging.getLogger("MangaPDFConverter")


def cleanup_empty_directories_recursive(root_path):
    """
    recursively remove all empty directories starting from root_path.
    returns True if the root_path directory itself was removed, False otherwise.

    Args:
        root_path (str): directory path to clean up.

    Returns:
        bool: True if root_path was removed, False otherwise.
    """
    # check if root_path exists and is a directory
    if not os.path.exists(root_path) or not os.path.isdir(root_path):
        return False

    removed_root = False

    try:
        # iterate over directory contents
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            # recursively clean subdirectories
            if os.path.isdir(item_path):
                cleanup_empty_directories_recursive(item_path)
    except OSError as e:
        logger.debug(f"error listing directory {root_path}: {e}")

    try:
        # if directory is empty after cleaning, remove it
        if os.path.exists(root_path) and not os.listdir(root_path):
            os.rmdir(root_path)
            logger.info(f"removed empty directory: {root_path}")
            removed_root = True
    except OSError as e:
        logger.debug(f"could not remove directory {root_path}: {e}")

    return removed_root
