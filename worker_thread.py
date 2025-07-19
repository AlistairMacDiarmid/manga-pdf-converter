from PyQt5.QtCore import QThread, pyqtSignal

from manga_pdf_converter import process_volumes, process_chapters, process_hybrid

class WorkerThread(QThread):
    """
    worker thread for processing
    this prevents GUI from freezing during long operations
    """
    # define signals
    progress_update = pyqtSignal(str)  # used for status messages
    finished_signal = pyqtSignal(bool, str)  # for completion (success, message)

    def __init__(self, path, mode, delete_images, settings = None):
        super().__init__()
        self.path = path
        self.mode = mode
        self.delete_images = delete_images
        self.settings = settings or {}
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        """
        run in a separate thread
        NEVER UPDATE UI FROM HERE - USE SIGNALS!!!!
        """
        try:
            self.progress_update.emit(f"starting conversion in {self.mode.upper()} mode")
            self.progress_update.emit(f"source: {self.path}")
            self.progress_update.emit(f"delete images: {'Yes' if self.delete_images else 'No'}")
            self.progress_update.emit("-" * 50)

            # function calls based on mode
            if self.mode == "volumes":
                process_volumes(self.path, self.delete_images, self.settings)
            elif self.mode == "chapters":
                process_chapters(self.path, self.delete_images, self.settings)
            else:  # hybrid
                process_hybrid(self.path, self.delete_images, self.settings)

            if not self.is_cancelled:
                self.finished_signal.emit(True, "conversion completed successfully!")

        except Exception as e:
            if not self.is_cancelled:
                self.finished_signal.emit(False, f"conversion failed: {str(e)}")

