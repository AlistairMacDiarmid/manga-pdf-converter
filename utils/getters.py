import os
import re
import logging
from collections import defaultdict

logger = logging.getLogger("MangaPDFConverter")


def get_all_retrace_folders(root):
    """
    find folders named like 'v1', 'vol. 2', 'volume 3', etc., and group them by volume.
    returns a dict like {'v1': [folder_path1, folder_path2], ...}

    Args:
        root (str): root directory to search for volume folders.

    Returns:
        defaultdict(list): mapping volume names to lists of folder paths.
    """
    # regex to match volume folder names (e.g., v1, vol.2, volume 3)
    retrace_pattern = re.compile(r'^(v|vol|volume)\.?\s*(\d+)', re.IGNORECASE)
    volumes = defaultdict(list)

    try:
        # list all items in root, sorted alphabetically
        for folder in sorted(os.listdir(root)):
            full_path = os.path.join(root, folder)
            if os.path.isdir(full_path):
                match = retrace_pattern.match(folder)
                if match:
                    volume_number = match.group(2)
                    volume_name = f"v{volume_number}"
                    volumes[volume_name].append(full_path)
    except OSError as e:
        logger.error(f"error accessing directory {root}: {e}")
        # return empty defaultdict on error
        return defaultdict(list)

    return volumes


def get_all_chapter_folders(root):
    """
    get all immediate subdirectories in root for chapter mode.
    returns a list of (folder_name, folder_path) tuples.

    Args:
        root (str): root directory to search for chapter folders.

    Returns:
        list of tuples: each tuple contains (folder_name, folder_path).
    """
    chapters = []
    try:
        # list and sort all items in root
        for folder in sorted(os.listdir(root)):
            full_path = os.path.join(root, folder)
            if os.path.isdir(full_path):
                chapters.append((folder, full_path))
    except OSError as e:
        logger.error(f"error accessing directory {root}: {e}")
        # return empty list on error
        return []

    return chapters


def get_hybrid_groups(root):
    """
    group folders based on volume/chapter naming or treat as standalone.
    returns a dict like {'Volume 1': [paths], 'Standalone Chapter': [path], ...}

    Args:
        root (str): root directory to search for hybrid groups.

    Returns:
        defaultdict(list): mapping group names to lists of folder paths.
    """
    hybrid_groups = defaultdict(list)
    # pattern for volume+chapter folder names (e.g., "volume 1 chapter 3")
    volume_chapter_pattern = re.compile(r'^volume\s+(\d+)\s+chapter\s+\d+', re.IGNORECASE)
    # simpler pattern for volume folder names (e.g., "v1", "vol. 2")
    simple_volume_pattern = re.compile(r'^(v|vol|volume)\.?\s*(\d+)', re.IGNORECASE)

    try:
        # list all folders sorted alphabetically
        for folder in sorted(os.listdir(root)):
            full_path = os.path.join(root, folder)
            if os.path.isdir(full_path):
                volume_chapter_match = volume_chapter_pattern.match(folder)
                if volume_chapter_match:
                    volume_key = f"Volume {volume_chapter_match.group(1)}"
                    hybrid_groups[volume_key].append(full_path)
                else:
                    simple_volume_match = simple_volume_pattern.match(folder)
                    if simple_volume_match:
                        volume_key = f"Volume {simple_volume_match.group(2)}"
                        hybrid_groups[volume_key].append(full_path)
                    else:
                        # sanitize folder name for safe use as key
                        safe_name = re.sub(r'[<>:"/\\|?*]', '_', folder)
                        hybrid_groups[safe_name].append(full_path)
    except OSError as e:
        logger.error(f"error accessing directory {root}: {e}")
        return defaultdict(list)

    return hybrid_groups


def get_image_files_recursive(folder):
    """
    recursively find all supported image files inside folder.
    returns a sorted list of image file paths.

    Args:
        folder (str): root folder to recursively search for images.

    Returns:
        list: sorted list of image file paths.
    """
    # supported image file extensions (case-insensitive)
    supported = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')
    files = []

    try:
        # walk directory tree
        for dirpath, _, filenames in os.walk(folder):
            for filename in sorted(filenames):
                if filename.lower().endswith(supported):
                    files.append(os.path.join(dirpath, filename))
    except OSError as e:
        logger.error(f"error walking directory {folder}: {e}")
        return []

    return files
