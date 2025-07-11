import os
import platform
import re
import zipfile
import tempfile
import subprocess
import logging
from PIL import Image

from utils.getters import get_image_files_recursive

logger = logging.getLogger("MangaPDFConverter")


def convert_images_to_pdf(image_paths, output_pdf_path, delete_originals=False, settings=None):
    """
    Convert a list of images to a single PDF file.

    Args:
        image_paths (list): List of image file paths to convert.
        output_pdf_path (str): Path to save the resulting PDF.
        delete_originals (bool): Whether to delete original images after conversion.
        settings (dict): Optional settings controlling image processing and PDF creation.
    """
    # Use default settings if none provided
    settings = settings or {}
    image_processing = settings.get("image_processing", "keep_original")
    resize_enabled = settings.get("resize_images", False)
    max_width = settings.get("max_width", 1920)
    max_height = settings.get("max_height", 1080)
    quality = settings.get("pdf_quality", 85)
    auto_open = settings.get("auto_open_pdf", False)
    backup = settings.get("backup_originals", False)
    delete_after = settings.get("delete_after_conversion", False)

    logger.info(f"starting conversion of {len(image_paths)} images to pdf: {output_pdf_path}")
    logger.debug(
        f"settings: resize_enabled={resize_enabled}, max_width={max_width}, max_height={max_height}, "
        f"image_processing={image_processing}, quality={quality}, backup={backup}, "
        f"delete_originals={delete_originals}, delete_after={delete_after}"
    )

    images = []
    for img_path in image_paths:
        logger.debug(f"processing image: {img_path}")
        try:
            # open and convert image to RGB mode
            img = Image.open(img_path).convert("RGB")
            original_size = img.size

            # resize image if enabled
            if resize_enabled:
                img.thumbnail((max_width, max_height), Image.ANTIALIAS)
                logger.debug(f"resized image from {original_size} to {img.size}")

            # re-save image in requested format temporarily, then re-open for consistent processing
            if image_processing == "jpeg":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    img.save(temp_file.name, "JPEG", quality=quality)
                    logger.debug(f"saved intermediate jpeg image at {temp_file.name} with quality={quality}")
                    img = Image.open(temp_file.name).convert("RGB")
            elif image_processing == "png":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    img.save(temp_file.name, "PNG")
                    logger.debug(f"saved intermediate png image at {temp_file.name}")
                    img = Image.open(temp_file.name).convert("RGB")

            images.append(img)
        except Exception as e:
            logger.error(f"failed to process image {img_path}: {e}")

    if not images:
        logger.error("no valid images found after processing. aborting pdf creation.")
        raise Exception("no valid images to convert")

    logger.info(f"saving {len(images)} images into pdf file: {output_pdf_path}")
    try:
        # save all images as multi-page PDF
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
    except Exception as e:
        logger.error(f"failed to save pdf file: {e}")
        raise Exception(f"failed to save pdf: {e}")

    # backup original images to zip if requested
    if backup and delete_originals:
        zip_path = output_pdf_path.replace(".pdf", "_backup.zip")
        logger.info(f"creating backup zip of original images at: {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for path in image_paths:
                    if os.path.exists(path):
                        zipf.write(path, os.path.basename(path))
                        logger.debug(f"added {path} to backup zip")
                    else:
                        logger.warning(f"original file missing during backup: {path}")
        except Exception as e:
            logger.warning(f"could not backup originals: {e}")

    # delete original images if requested
    if delete_originals or delete_after:
        logger.info("deleting original images after conversion")
        for path in image_paths:
            try:
                os.remove(path)
                logger.debug(f"deleted image file: {path}")
            except Exception as e:
                logger.warning(f"could not delete image {path}: {e}")

    # automatically open PDF if requested
    if auto_open:
        logger.info(f"attempting to open pdf automatically: {output_pdf_path}")
        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", output_pdf_path], check=True)
            elif platform.system() == "Windows":
                os.startfile(output_pdf_path)
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", output_pdf_path], check=True)
            logger.info("pdf opened successfully")
        except Exception as e:
            logger.warning(f"could not open pdf: {e}")


def process_folder_groups(folder_groups, output_dir, delete_images=False, settings=None):
    """
    Process multiple groups of folders, converting all images inside each group into a PDF.

    Args:
        folder_groups (dict): Dictionary mapping group names to lists of folder paths.
        output_dir (str): Directory to save the resulting PDFs.
        delete_images (bool): Whether to delete images after conversion.
        settings (dict): Optional settings for image processing and PDF creation.
    """
    logger.info(f"📦 processing {len(folder_groups)} folder groups into pdfs...")

    for group_name, folders in sorted(folder_groups.items()):
        logger.info(f"\n📁 starting group: '{group_name}' ({len(folders)} folder{'s' if len(folders) > 1 else ''})")

        all_images = []
        for folder in sorted(folders):
            logger.debug(f"🔍 scanning for images in: {folder}")
            images = get_image_files_recursive(folder)
            all_images.extend(images)

        if not all_images:
            logger.warning(f"⚠️ no images found in group '{group_name}'. skipping.")
            continue

        logger.info(f"🖼️ found {len(all_images)} total images for group '{group_name}'")

        # sanitize group name to safe file name
        safe_group_name = re.sub(r'[<>:"/\\|?*]', '_', group_name)
        output_pdf = os.path.join(output_dir, f"{safe_group_name}.pdf")

        try:
            logger.info(f"📤 converting images to pdf: {output_pdf}")
            convert_images_to_pdf(all_images, output_pdf, delete_images, settings)
            logger.info(f"✅ pdf created for group '{group_name}': {output_pdf}")
        except Exception as e:
            logger.error(f"❌ failed to create pdf for group '{group_name}': {e}")
