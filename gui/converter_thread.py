from PyQt5.QtCore import QThread, pyqtSignal
import logging

logger = logging.getLogger("MangaPDFConverter")


class ConverterThread(QThread):
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, path, mode, delete_images, debug, settings=None):
        super().__init__()
        self.path = path
        self.mode = mode
        self.delete_images = delete_images
        self.debug = debug
        self.settings = settings

    def run(self):
        try:
            #set up debug logging if requested
            if self.debug:
                logging.getLogger("MangaPDFConverter").setLevel(logging.DEBUG)
            else:
                logging.getLogger("MangaPDFConverter").setLevel(logging.INFO)

            #import  processing functions
            from processing_modes.modes import process_volumes, process_chapters, process_hybrid

            #run appropriate processing function based on mode
            if self.mode == "volumes":
                success = self._safe_process(process_volumes)
            elif self.mode == "chapters":
                success = self._safe_process(process_chapters)
            elif self.mode == "hybrid":
                success = self._safe_process(process_hybrid)
            else:
                self.error_occurred.emit(f"Unknown processing mode: {self.mode}")
                return

            if not success:
                self.error_occurred.emit("processing completed with errors. Check the logs for details.")

        except Exception as e:
            logger.exception(f"unexpected error during conversion: {e}")
            self.error_occurred.emit(f"conversion failed: {str(e)}")
        finally:
            self.finished.emit()

    def _safe_process(self, process_func):
        """
        safely execute a processing function and return True if successful.
        """
        try:
            process_func(self.path, self.delete_images, self.settings)
            return True
        except FileNotFoundError as e:
            logger.error(f"file or directory not found: {e}")
            self.error_occurred.emit(f"file not found: {str(e)}")
            return False
        except PermissionError as e:
            logger.error(f"permission denied: {e}")
            self.error_occurred.emit(f"permission denied: {str(e)}")
            return False
        except OSError as e:
            logger.error(f"system error: {e}")
            self.error_occurred.emit(f"system error: {str(e)}")
            return False
        except Exception as e:
            logger.exception(f"error in {process_func.__name__}: {e}")
            self.error_occurred.emit(f"processing error: {str(e)}")
            return False