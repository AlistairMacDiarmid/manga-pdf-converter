# imports
import json
import logging
import os
import sys


from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QObject
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, \
    QLineEdit, QPushButton, QFileDialog, QGroupBox, QRadioButton, QCheckBox, QProgressBar, \
    QTextEdit, QMessageBox, QTabWidget, QButtonGroup, QGraphicsBlurEffect
from manga_pdf_converter import process_volumes, process_chapters, process_hybrid

SETTINGS_FILE = "settings.json"
DARK_THEME_STYLESHEET = """
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget#centralWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QScrollArea {
                border: none;
                background-color: #2b2b2b;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 10px;
                margin-top: 1ex;
                margin-left: 10px;
                margin-right: 10px;
                padding-top: 10px;
                background-color: #353535;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #777777;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
                border-color: #333333;
            }
            QLineEdit {
                background-color: #404040;
                border: 2px solid #555555;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 12px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 4px;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
            QRadioButton {
                color: #ffffff;
                spacing: 8px;
                font-size: 12px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: #2b2b2b;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #0078d4;
                border-radius: 8px;
                background-color: #0078d4;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #555555;
                border-radius: 3px;
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #0078d4;
                border-radius: 3px;
                background-color: #0078d4;
            }
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                background-color: #2b2b2b;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            QLabel {
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 2px solid #555555;
                border-radius: 6px;
                background-color: #2b2b2b;
                top: -2px;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background-color: #404040;
                border: 2px solid #555555;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                color: #ffffff;
                font-weight: bold;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                border-color: #555555;
                color: #0078d4;
            }
            QTabBar::tab:hover:!selected {
                background-color: #505050;
                border-color: #777777;
            }
            QTabBar::tab:disabled {
                background-color: #2a2a2a;
                color: #666666;
                border-color: #333333;
            }
        """
LIGHT_THEME_STYLESHEET = """
            QMainWindow {
                background-color: #f5f5f5;
                color: #2d2d2d;
            }
            QWidget#centralWidget {
                background-color: #f5f5f5;
                color: #2d2d2d;
            }
            QWidget {
                background-color: #f5f5f5;
                color: #2d2d2d;
            }
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c0c0c0;
                border-radius: 10px;
                margin-top: 1ex;
                margin-left: 10px;
                margin-right: 10px;
                padding-top: 10px;
                background-color: #ffffff;
                color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 5px 0 5px;
                color: #2d2d2d;
            }
            QPushButton {
                background-color: #e8e8e8;
                border: 2px solid #b0b0b0;
                border-radius: 6px;
                padding: 8px 16px;
                color: #2d2d2d;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
                border-color: #909090;
            }
            QPushButton:pressed {
                background-color: #c8c8c8;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #a0a0a0;
                border-color: #d0d0d0;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #b0b0b0;
                border-radius: 4px;
                padding: 8px;
                color: #2d2d2d;
                font-size: 12px;
            }
            QTextEdit {
                background-color: #fafafa;
                border: 2px solid #b0b0b0;
                border-radius: 4px;
                color: #2d2d2d;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
            QRadioButton {
                color: #2d2d2d;
                spacing: 8px;
                font-size: 12px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #b0b0b0;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #0078d4;
                border-radius: 8px;
                background-color: #0078d4;
            }
            QCheckBox {
                color: #2d2d2d;
                spacing: 8px;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #b0b0b0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #0078d4;
                border-radius: 3px;
                background-color: #0078d4;
            }
            QProgressBar {
                border: 2px solid #b0b0b0;
                border-radius: 5px;
                background-color: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            QLabel {
                color: #2d2d2d;
            }
              QTabWidget::pane {
                border: 2px solid #cccccc;
                border-radius: 6px;
                background-color: #ffffff;
                top: -2px;        
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                color: #333333;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-color: #cccccc;
                color: #0078d4;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e8e8e8;
                border-color: #999999;
            }
            QTabBar::tab:disabled {
                background-color: #f5f5f5;
                color: #999999;
                border-color: #e0e0e0;
            }
        """


class QTextEditLogger(logging.Handler, QObject):
    new_log = pyqtSignal(str)

    def __init__(self, parent=None):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.widget = None

    def emit(self, record):
        msg = self.format(record)
        if self.widget:
            self.new_log.emit(msg)

    def setWidget(self, widget):
        self.widget = widget
        self.new_log.connect(widget.append)


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


class SettingsGUI(QWidget):

    finished = pyqtSignal()
    settings_saved = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.parent = parent
        self.current_settings = current_settings or self.get_default_settings()
        self.is_dark = self.current_settings.get("theme", "dark") == "dark"
        self.init_ui()
        self.apply_theme()
        self.load_settings()
        self._settings_saved = False

    def themed(self, bg=None, fg=None):
        bg = bg or ("#353535" if self.is_dark else "#ffffff")
        fg = fg or ("#ffffff" if self.is_dark else "#2b2b2b")
        return f"background-color: {bg}; color: {fg};"

    def get_default_settings(self):
        """returns the default settings"""
        return {
            'pdf_quality': 85,
            'image_processing': 'keep_original',
            'pdf_compression': True,
            'resize_images': False,
            'max_width': 1920,
            'max_height': 1080,
            'output_folder': '',
            'auto_open_pdf': False,
            'backup_originals': False,
            'delete_after_conversion': False,
            'theme' : 'dark'
        }

    def init_ui(self):
        self.setWindowTitle("settings")
        self.setFixedSize(650,600)
        self.setWindowModality(Qt.ApplicationModal)

        #main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        #create the tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        #PDF settings tab
        pdf_tab = self.create_pdf_settings_tab()
        tab_widget.addTab(pdf_tab, "PDF settings")

        #image settings tab
        image_tab = self.create_image_settings_tab()
        tab_widget.addTab(image_tab, "image processing")

        #output settings tab
        output_tab = self.create_output_settings_tab()
        tab_widget.addTab(output_tab, "output settings")

        #buttons at bottom
        button_layout = QHBoxLayout()

        reset_btn = QPushButton("reset to defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)

        cancel_btn = QPushButton("cancel")
        cancel_btn.clicked.connect(self.close)

        save_btn = QPushButton("save")
        save_btn.clicked.connect(self.save_settings)

        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        main_layout.addLayout(button_layout)

        appearance_tab = self.create_appearance_settings_tab()
        tab_widget.addTab(appearance_tab, "appearance")

    def create_pdf_settings_tab(self):
        """create PDF settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        #PDF quality
        quality_group = QGroupBox("PDF Quality")
        quality_layout = QVBoxLayout()
        quality_group.setLayout(quality_layout)

        quality_label = QLabel("quality (1-100):")
        self.quality_input = QLineEdit()
        self.quality_input.setPlaceholderText("85")
        quality_label.setStyleSheet(f"{self.themed()}")

        quality_desc = QLabel("higher values = better quality but larger file size")
        quality_desc.setStyleSheet(f"font-size: 11px;{self.themed()}")

        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_input)
        quality_layout.addWidget(quality_desc)
        layout.addWidget(quality_group)

        #PDF options
        options_group = QGroupBox("PDF Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)

        self.compression_checkbox = QCheckBox("Enable PDF compression")
        self.compression_checkbox.setStyleSheet(self.themed())
        options_layout.addWidget(self.compression_checkbox)

        layout.addWidget(options_group)
        layout.addStretch()

        return tab

    def create_image_settings_tab(self):
        """create image processing settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        #image Processing
        processing_group = QGroupBox("image processing")
        processing_layout = QVBoxLayout()
        processing_group.setLayout(processing_layout)

        process_desc = QLabel("how input images should be processed before adding to PDF:")
        process_desc.setStyleSheet(f"font-size: 12px; margin-bottom: 10px;{self.themed()}")
        processing_layout.addWidget(process_desc)

        self.format_group = QButtonGroup()

        self.keep_original_radio = QRadioButton("keep original format (fastest)")
        self.keep_original_radio.setStyleSheet(self.themed())
        self.jpeg_radio = QRadioButton("convert to JPEG (smaller PDF size)")
        self.jpeg_radio.setStyleSheet(self.themed())
        self.png_radio = QRadioButton("convert to PNG (preserve transparency)")
        self.png_radio.setStyleSheet(self.themed())

        self.format_group.addButton(self.keep_original_radio, 0)
        self.format_group.addButton(self.jpeg_radio, 1)
        self.format_group.addButton(self.png_radio, 2)

        processing_layout.addWidget(self.keep_original_radio)
        processing_layout.addWidget(self.jpeg_radio)
        processing_layout.addWidget(self.png_radio)
        layout.addWidget(processing_group)

        #resolution settings
        resolution_group = QGroupBox("image resolution limits")
        resolution_layout = QVBoxLayout()
        resolution_group.setLayout(resolution_layout)

        res_desc = QLabel("resize large images to reduce PDF file size:")
        res_desc.setStyleSheet(f"font-size: 12px; margin-bottom: 10px;{self.themed()}")
        resolution_layout.addWidget(res_desc)

        self.resize_checkbox = QCheckBox("enable image resizing")
        self.resize_checkbox.setStyleSheet(self.themed())
        resolution_layout.addWidget(self.resize_checkbox)

        size_layout = QHBoxLayout()

        width_label = QLabel("max width:")
        width_label.setStyleSheet(f"{self.themed()}")
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("1920")
        self.width_input.setEnabled(False)

        height_label = QLabel("max height:")
        height_label.setStyleSheet(f"{self.themed()}")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("1080")
        self.height_input.setEnabled(False)

        size_layout.addWidget(width_label)
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(height_label)
        size_layout.addWidget(self.height_input)

        resolution_layout.addLayout(size_layout)

        #connect checkbox to enable/disable inputs
        self.resize_checkbox.toggled.connect(self.width_input.setEnabled)
        self.resize_checkbox.toggled.connect(self.height_input.setEnabled)

        layout.addWidget(resolution_group)
        layout.addStretch()
        return tab

    def create_output_settings_tab(self):
        """create output settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        #output Folder
        folder_group = QGroupBox("output location")
        folder_layout = QVBoxLayout()
        folder_group.setLayout(folder_layout)

        folder_label = QLabel("custom output folder (optional):")
        folder_label.setStyleSheet(f"{self.themed()}")
        folder_layout.addWidget(folder_label)

        folder_input_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setPlaceholderText("leave empty to use source folder")
        folder_input_layout.addWidget(self.output_folder_input)

        browse_output_btn = QPushButton("browse")
        browse_output_btn.clicked.connect(self.browse_output_folder)
        folder_input_layout.addWidget(browse_output_btn)

        folder_layout.addLayout(folder_input_layout)
        layout.addWidget(folder_group)

        #behavior Options
        behavior_group = QGroupBox("behavior")
        behavior_layout = QVBoxLayout()
        behavior_group.setLayout(behavior_layout)

        self.auto_open_checkbox = QCheckBox("auto-open PDF files after conversion")
        self.auto_open_checkbox.setStyleSheet(self.themed())
        self.backup_checkbox = QCheckBox("create backup of original images before conversion")
        self.backup_checkbox.setStyleSheet(self.themed())
        self.delete_checkbox = QCheckBox("delete source images after successful conversion")
        self.delete_checkbox.setStyleSheet(self.themed())

        delete_warning = QLabel("⚠️ warning: deletion cannot be undone!")
        delete_warning.setStyleSheet(f"font-size: 12px; font-weight: bold;{self.themed()} color:#d32f2f;")

        behavior_layout.addWidget(self.auto_open_checkbox)
        behavior_layout.addWidget(self.backup_checkbox)
        behavior_layout.addWidget(self.delete_checkbox)
        behavior_layout.addWidget(delete_warning)
        layout.addWidget(behavior_group)

        layout.addStretch()
        return tab

    def create_appearance_settings_tab(self):
        """create the tab which allows the user to change the application appearance"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        appearance_group = QGroupBox("theme")
        appearance_layout = QVBoxLayout()
        appearance_group.setLayout(appearance_layout)

        self.theme_group = QButtonGroup()
        self.dark_theme_radio = QRadioButton("dark")
        self.dark_theme_radio.setStyleSheet(self.themed())
        self.light_theme_radio = QRadioButton("light")
        self.light_theme_radio.setStyleSheet(self.themed())

        self.theme_group.addButton(self.dark_theme_radio)
        self.theme_group.addButton(self.light_theme_radio)

        appearance_layout.addWidget(self.dark_theme_radio)
        appearance_layout.addWidget(self.light_theme_radio)

        layout.addWidget(appearance_group)
        layout.addStretch()

        return tab

    def apply_theme(self):
        theme = self.current_settings.get("theme", "dark")
        if theme == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)

    def load_settings(self):
        """load current settings into the UI"""
        self.quality_input.setText(str(self.current_settings.get('pdf_quality', 85)))
        self.width_input.setText(str(self.current_settings.get('max_width', 1920)))
        self.height_input.setText(str(self.current_settings.get('max_height', 1080)))
        self.output_folder_input.setText(self.current_settings.get('output_folder', ''))
        self.auto_open_checkbox.setChecked(self.current_settings.get('auto_open_pdf', False))
        self.backup_checkbox.setChecked(self.current_settings.get('backup_originals', False))
        self.delete_checkbox.setChecked(self.current_settings.get('delete_after_conversion', False))
        self.compression_checkbox.setChecked(self.current_settings.get('pdf_compression', True))
        self.resize_checkbox.setChecked(self.current_settings.get('resize_images', False))

        theme = self.current_settings.get('theme', 'dark')
        if theme == 'light':
            self.light_theme_radio.setChecked(True)
        else:
            self.dark_theme_radio.setChecked(True)

        #set image processing radio button
        processing_type = self.current_settings.get('image_processing', 'keep_original')
        if processing_type == 'png':
            self.png_radio.setChecked(True)
        elif processing_type == 'jpeg':
            self.jpeg_radio.setChecked(True)
        else:
            self.keep_original_radio.setChecked(True)

    def browse_output_folder(self):
        """browse for output folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "select output folder",
            os.path.expanduser("~")
        )
        if folder:
            self.output_folder_input.setText(folder)

    def validate_settings(self):
        """validate the settings before saving"""
        try:
            quality = int(self.quality_input.text()) if self.quality_input.text() else 85
            if not (1 <= quality <= 100):
                QMessageBox.warning(self, "invalid setting", "PDF quality must be between 1 and 100")
                return False

            width = int(self.width_input.text()) if self.width_input.text() else 1920
            height = int(self.height_input.text()) if self.height_input.text() else 1080

            if width < 100 or height < 100:
                QMessageBox.warning(self, "invalid setting", "width and height must be at least 100 pixels")
                return False

            return True
        except ValueError:
            QMessageBox.warning(self, "invalid setting", "please enter valid numbers for quality, width, and height")
            return False

    def save_settings(self):
        """save the settings and mark that they've been saved"""
        if not self.validate_settings():
            return

        # get selected image processing method
        if self.png_radio.isChecked():
            image_processing = 'png'
        elif self.jpeg_radio.isChecked():
            image_processing = 'jpeg'
        else:
            image_processing = 'keep_original'

        theme = 'light' if self.light_theme_radio.isChecked() else 'dark'

        # update settings dictionary
        self.current_settings.update({
            'pdf_quality': int(self.quality_input.text()) if self.quality_input.text() else 85,
            'max_width': int(self.width_input.text()) if self.width_input.text() else 1920,
            'max_height': int(self.height_input.text()) if self.height_input.text() else 1080,
            'output_folder': self.output_folder_input.text(),
            'auto_open_pdf': self.auto_open_checkbox.isChecked(),
            'backup_originals': self.backup_checkbox.isChecked(),
            'delete_after_conversion': self.delete_checkbox.isChecked(),
            'pdf_compression': self.compression_checkbox.isChecked(),
            'resize_images': self.resize_checkbox.isChecked(),
            'image_processing': image_processing,
            'theme': theme
        })

        # update parent window if it exists
        if self.parent and hasattr(self.parent, 'settings'):
            self.parent.settings = self.current_settings

        self.apply_theme()
        self._settings_saved = True  #mark that settings were saved
        self.close()  #trigger closeEvent

    def reset_to_defaults(self):
        """reset all settings to defaults"""
        reply = QMessageBox.question(self, "reset settings",
                                     "are you sure you want to reset all settings to defaults?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.current_settings = self.get_default_settings()
            self.load_settings()

    def get_settings(self):
        """return current settings"""
        return self.current_settings

    def closeEvent(self, event):
        """override close event to handle both save and cancel cases"""
        if not hasattr(self, '_closing'):
            self._closing = True
            if self._settings_saved:
                self.finished.emit()  # only emit finished if saved
            else:
                self.cancelled.emit()  #emit cancelled otherwise
        super().closeEvent(event)

    def accept(self):
        """override accept - this should not be called directly"""
        #just close the window, the closeEvent will handle the signal
        self.close()

class MangaConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.convert_btn = None
        self.status_label = None
        self.delete_checkbox = None
        self.cancel_btn = None
        self.warning_label = None
        self.clear_log_button = None
        self.progress_bar = None
        self.path_input = None
        self.chapter_radio = None
        self.volume_radio = None
        self.hybrid_radio = None
        self.process_mode_group = None
        self.selected_path = ""
        self.worker_thread = None
        self.settings = {}
        self.load_settings_from_file()
        self.is_dark = self.settings.get('theme', "dark") == "dark"
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        # set the window properties
        self.setWindowTitle("Manga PDF converter")
        self.setGeometry(0, 0, 650, 900)

        # create central widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        # create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # title label
        title = QLabel("manga to PDF converter")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:16px; font-weight:bold; margin:15px")
        main_layout.addWidget(title)

        # file selection section
        file_selection = self.create_file_selection_section()
        main_layout.addWidget(file_selection)

        # spacing between widgets
        main_layout.addSpacing(10)

        # processing mode selection
        mode_selection = self.create_process_mode_selection_section()
        main_layout.addWidget(mode_selection)

        # spacing between widgets
        main_layout.addSpacing(10)

        # options section - currently only delete images after conversion
        options_section = self.create_options_section()
        main_layout.addWidget(options_section)

        # spacing between widgets
        main_layout.addSpacing(10)

        # control buttons
        controls_section = self.create_controls_section()
        main_layout.addWidget(controls_section)

        # spacing between widgets
        main_layout.addSpacing(10)

        # status label
        self.status_label = QLabel("Ready to convert")
        self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(15)
        main_layout.addWidget(self.status_label)

        # progress and log section
        progress_section = self.create_progress_section()
        main_layout.addWidget(progress_section)

        # stretch to push everything to top
        main_layout.addStretch()

    def apply_theme(self):
        """apply a different theme to the application"""
        theme = self.settings.get("theme", "dark")
        if theme == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)

    def themed(self, bg=None, fg=None):
        bg = bg or ("#353535" if self.is_dark else "#ffffff")
        fg = fg or ("#ffffff" if self.is_dark else "#2b2b2b")
        return f"background-color: {bg}; color: {fg};"

    def create_file_selection_section(self):
        # create group widget
        file_selection_section = QGroupBox("folder selection")
        file_selection_section_layout = QVBoxLayout()
        file_selection_section.setLayout(file_selection_section_layout)

        # horizontal layout for path input and browse button
        path_layout = QHBoxLayout()

        # path input field
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("choose the mangas folder...")
        path_layout.addWidget(self.path_input)

        # browse button
        browse_btn = QPushButton("browse")
        browse_btn.clicked.connect(self.browse_folder)  # signal-slot connection
        path_layout.addWidget(browse_btn)

        file_selection_section_layout.addLayout(path_layout)

        # return widget
        return file_selection_section

    def create_process_mode_selection_section(self):
        # create group widget
        mode_selection_section = QGroupBox("mode selection")
        mode_selection_section_layout = QVBoxLayout()
        mode_selection_section.setLayout(mode_selection_section_layout)

        # create button group and radio buttons
        self.process_mode_group = QButtonGroup()
        self.hybrid_radio = QRadioButton("hybrid (recommended)")
        self.hybrid_radio.setChecked(True)  # set as default
        self.volume_radio = QRadioButton("volumes")
        self.chapter_radio = QRadioButton("chapters")

        # add buttons to group
        self.process_mode_group.addButton(self.hybrid_radio, 0)
        self.process_mode_group.addButton(self.volume_radio, 1)
        self.process_mode_group.addButton(self.chapter_radio, 2)

        # radio button layout
        radio_btn_widget = QWidget()
        radio_btn_layout = QHBoxLayout()
        radio_btn_layout.setSpacing(30)
        radio_btn_widget.setLayout(radio_btn_layout)

        radio_btn_layout.addWidget(self.hybrid_radio)
        radio_btn_layout.addWidget(self.volume_radio)
        radio_btn_layout.addWidget(self.chapter_radio)

        radio_btn_widget.setStyleSheet(self.themed())

        # add radio button widget to groupbox
        mode_selection_section_layout.addWidget(radio_btn_widget)

        # add descriptions for each processing mode
        mode_desc_label = QLabel("☆ hybrid: groups volumes and treats other folders as individual chapters\n"
                                 "☆ volumes: groups folders by volume names (v1, v2, etc)\n"
                                 "☆ chapters: each folder becomes a separate pdf")

        mode_desc_label.setStyleSheet(f"font-size: 12px; {self.themed()}")
        mode_desc_label.setWordWrap(True);

        mode_selection_section_layout.addWidget(mode_desc_label)

        return mode_selection_section

    def create_options_section(self):
        # create groupbox
        options_group_box = QGroupBox("options")
        options_group_layout = QVBoxLayout()
        options_group_box.setLayout(options_group_layout)

        # checkbox for image deletion after conversion
        self.delete_checkbox = QCheckBox("delete source images after conversion")
        self.delete_checkbox.setStyleSheet(self.themed())
        options_group_layout.addWidget(self.delete_checkbox)

        self.warning_label = QLabel("⚠️ warning: this will permanently delete the image files")
        self.warning_label.setStyleSheet(f"{self.themed()} color:#d32f2f")
        options_group_layout.addWidget(self.warning_label)

        return options_group_box

    def create_controls_section(self):
        controls_group_box = QGroupBox("controls")
        controls_group_layout = QHBoxLayout()
        controls_group_box.setLayout(controls_group_layout)

        # convert button
        self.convert_btn = QPushButton("convert")
        self.convert_btn.clicked.connect(self.start_conversion)
        controls_group_layout.addWidget(self.convert_btn)

        # cancel button
        self.cancel_btn = QPushButton("cancel")
        self.cancel_btn.clicked.connect(self.cancel_conversion)
        self.cancel_btn.setEnabled(False)
        controls_group_layout.addWidget(self.cancel_btn)

        # settings button
        settings_btn = QPushButton("settings")
        settings_btn.clicked.connect(self.open_settings)
        controls_group_layout.addWidget(settings_btn)

        controls_group_layout.addStretch()
        return controls_group_box

    def create_progress_section(self):
        progress_group_box = QGroupBox("logging")
        progress_group_layout = QVBoxLayout()
        progress_group_box.setLayout(progress_group_layout)

        # progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_group_layout.addWidget(self.progress_bar)

        # logging area
        self.log_text_area = QTextEdit()
        self.log_text_area.setMaximumHeight(250)
        self.log_text_area.setFont(QFont("Monaco", 10))
        self.log_text_area.setReadOnly(True)
        progress_group_layout.addWidget(self.log_text_area)

        # logging setup
        self.log_handler = QTextEditLogger(self.log_text_area)
        self.log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.log_handler.setLevel(logging.DEBUG)

        logger = logging.getLogger("MangaPDFConverter")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.log_handler)

        # clear log button
        clear_button_layout = QHBoxLayout()
        clear_button_layout.addStretch()

        self.clear_log_button = QPushButton("clear log")
        self.clear_log_button.setMaximumWidth(100)
        self.clear_log_button.clicked.connect(self.clear_log)
        clear_button_layout.addWidget(self.clear_log_button)

        progress_group_layout.addLayout(clear_button_layout)

        return progress_group_box


    def clear_log(self):
        """Clear the log text area"""
        self.log_text_area.clear()

    def get_selected_mode(self):
        """
        get the currently selected processing mode
        """
        if self.hybrid_radio.isChecked():
            return "hybrid"
        elif self.volume_radio.isChecked():
            return "volumes"
        else:
            return "chapters"

    def start_conversion(self):
        """
        start the conversion process
        """
        # validate input
        if not self.selected_path:
            QMessageBox.warning(self, "warning", "please select a manga folder to convert")
            return
        if not os.path.isdir(self.selected_path):
            QMessageBox.warning(self, "warning", "please select a valid directory to convert")
            return
        # get the settings
        process_mode = self.get_selected_mode()
        delete_images = self.delete_checkbox.isChecked()

        # confirm the user wants to delete images after conversion
        if delete_images:
            reply = QMessageBox.question(self,
                                         "warning",
                                         "are you sure you want to delete image files?\n\n"
                                         "reminder that this cannot be undone :/",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

        # update the processing state UI
        self.convert_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # indeterminate progress

        # Update status label
        self.status_label.setText("processing...")
        self.status_label.setStyleSheet("color: orange; font-weight: bold; font-size: 14px;")

        self.log_text_area.clear()
        self.log_text_area.append(f'starting conversion in {process_mode} mode')

        #reload settings
        self.load_settings_from_file()

        # create and start the worker thread
        self.worker_thread = WorkerThread(self.selected_path, process_mode, delete_images,self.settings)
        self.worker_thread.progress_update.connect(self.update_progress)
        self.worker_thread.finished_signal.connect(self.conversion_finished)
        self.worker_thread.start()

    def update_progress(self, message):
        """
        update the progress display
        called from the worker thread
        :param message:
        """
        self.log_text_area.append(message)
        # auto scroll to bottom
        self.log_text_area.verticalScrollBar().setValue(self.log_text_area.verticalScrollBar().maximum())

    def conversion_finished(self, success, message):
        """
        handle conversion completion
        """
        # update the UI
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        # show the result
        if success:
            self.log_text_area.append(f"{message}")
            self.status_label.setText("conversion completed successfully :)")
            self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
            QMessageBox.information(self, "conversion successful :)", message)
        else:
            self.log_text_area.append(f"{message}")
            self.status_label.setText("Conversion failed")
            self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
            QMessageBox.critical(self, "conversion failed", message)

        # clean up thread
        self.worker_thread = None

    def cancel_conversion(self):
        """
        cancel the conversion process
        """
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.wait(3000)  #wait up to 3 seconds for graceful shutdown
            if self.worker_thread.isRunning():
                self.worker_thread.terminate()  #force terminate if it doesn't stop
                self.worker_thread.wait()
            self.conversion_finished(False, "conversion cancelled by user")

    def browse_folder(self):
        """handle folder selection"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "select manga folder",
            os.path.expanduser("~")  # start in home directory
        )

        if folder:  # if user doesnt cancel
            self.selected_path = folder
            self.path_input.setText(folder)
            self.log_text_area.append(f"Selected folder: {folder}")

    def open_settings(self):
        """open the settings widget with proper signal connections"""
        #apply blur effect
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(0)
        self.centralWidget().setGraphicsEffect(self.blur_effect)

        #animate blur in
        self.blur_animation = QPropertyAnimation(self.blur_effect, b"blurRadius")
        self.blur_animation.setDuration(250)
        self.blur_animation.setStartValue(0)
        self.blur_animation.setEndValue(12)
        self.blur_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.blur_animation.start()

        #create settings window
        self.settings_window = SettingsGUI(parent=self, current_settings=self.settings.copy())
        self.settings_window.finished.connect(self.on_settings_saved)
        self.settings_window.cancelled.connect(self.on_settings_cancelled)  # Connect cancelled signal
        self.settings_window.show()

    def get_default_settings(self):
        """get default settings for the application"""
        return {
            'pdf_quality': 85,
            'image_processing': 'keep_original',
            'pdf_compression': True,
            'resize_images': False,
            'max_width': 1920,
            'max_height': 1080,
            'output_folder': '',
            'auto_open_pdf': False,
            'backup_originals': False,
            'delete_after_conversion': False,
            'theme': 'dark'
        }

    def load_settings_from_file(self):
        """load settings from JSON file"""
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    loaded_settings = json.load(f)
                    # merge with defaults to ensure all keys exist
                    self.settings = self.get_default_settings()
                    self.settings.update(loaded_settings)
                    # Only log if log_text_area exists
                    if hasattr(self, 'log_text_area'):
                        self.log_text_area.append(f"settings loaded from {SETTINGS_FILE}")
            else:
                self.settings = self.get_default_settings()
                if hasattr(self, 'log_text_area'):
                    self.log_text_area.append("using default settings (no settings file found)")
        except Exception as e:
            if hasattr(self, 'log_text_area'):
                self.log_text_area.append(f"error loading settings: {str(e)}")
            self.settings = self.get_default_settings()

    def save_settings_to_file(self):
        """save current settings to JSON file"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.log_text_area.append(f"settings saved to {SETTINGS_FILE}")
        except Exception as e:
            self.log_text_area.append(f"error saving settings: {str(e)}")
            QMessageBox.warning(self, "save error", f"could not save settings: {str(e)}")

    def on_settings_saved(self):
        """handle when settings are saved"""
        self.save_settings_to_file()
        self.is_dark = self.settings.get('theme', 'dark') == 'dark'
        self.remove_blur_effect()
        self.apply_theme()

    def on_settings_cancelled(self):
        """handle when settings are cancelled"""
        self.remove_blur_effect()

    def remove_blur_effect(self):
        """safely remove blur effect with animation"""
        if hasattr(self, 'blur_effect') and self.blur_effect:
            #animate blur out
            self.blur_out_animation = QPropertyAnimation(self.blur_effect, b"blurRadius")
            self.blur_out_animation.setDuration(200)
            self.blur_out_animation.setStartValue(12)
            self.blur_out_animation.setEndValue(0)
            self.blur_out_animation.setEasingCurve(QEasingCurve.InCubic)
            self.blur_out_animation.finished.connect(self.cleanup_blur_effect)
            self.blur_out_animation.start()

    def cleanup_blur_effect(self):
        """complete removal of blur effect"""
        if hasattr(self, 'blur_effect'):
            self.centralWidget().setGraphicsEffect(None)
            del self.blur_effect
        if hasattr(self, 'settings_window'):
            del self.settings_window


if __name__ == "__main__":
    # logging for debugging
    logging.basicConfig(level=logging.DEBUG)

    # create application
    app = QApplication(sys.argv)

    # set application icon
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass  #ignore if icon file doesn't exist


    # create and show window
    window = MangaConverterGUI()
    window.show()

    # start event loop
    sys.exit(app.exec_())