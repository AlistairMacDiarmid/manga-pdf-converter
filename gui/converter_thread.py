from PyQt5.QtCore import QThread
import logging

from processing_modes.modes import process_volumes, process_chapters, process_hybrid

logger = logging.getLogger("MangaPDFConverter")

class ConverterThread(QThread):
    def __init__(self, path, mode, delete_images, debug=False):
        super().__init__()
        self.path = path
        self.mode = mode
        self.delete_images = delete_images
        self.debug = debug

    def run(self):
        try:
            if self.debug:
                logger.setLevel(logging.DEBUG)

            logger.info(f"🔁 Starting conversion in {self.mode.upper()} mode")
            if self.mode == "volumes":
                process_volumes(self.path, self.delete_images, settings=self.settings)
            elif self.mode == "chapters":
                process_chapters(self.path, self.delete_images, settings=self.settings)
            else:
                process_hybrid(self.path, self.delete_images, settings=self.settings)

            logger.info("✅ All conversions finished successfully.")
        except Exception as e:
            logger.error(f"❌ Conversion failed: {e}")
