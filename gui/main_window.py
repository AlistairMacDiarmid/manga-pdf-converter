
from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QGroupBox, QRadioButton,
    QCheckBox, QTextEdit, QProgressBar, QAction, QGraphicsBlurEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from gui.converter_thread import ConverterThread
from gui.log_handler import QTextEditLogger
from gui.SettingsGUI import SettingsGUI
from utils.styles import load_stylesheet

import logging

from utils.settings import load_settings, save_settings

logger = logging.getLogger("MangaPDFConverter")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.apply_theme()

        # set window title and initial size
        self.setWindowTitle("Manga PDF Converter")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.converter_thread = None  # will hold background conversion thread


    def init_ui(self):
        """
        create and arrange UI widgets for the main window.
        """
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # input path selection controls
        input_layout = QHBoxLayout()
        self.input_path_edit = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_input)
        input_layout.addWidget(QLabel("Manga Folder:"))
        input_layout.addWidget(self.input_path_edit)
        input_layout.addWidget(browse_btn)
        layout.addLayout(input_layout)

        # conversion mode radio buttons grouped in QGroupBox
        self.mode_group = QGroupBox("Conversion Mode")
        mode_layout = QVBoxLayout()
        self.mode_radio_volumes = QRadioButton("Volumes")
        self.mode_radio_chapters = QRadioButton("Chapters")
        self.mode_radio_hybrid = QRadioButton("Hybrid")
        self.mode_radio_hybrid.setChecked(True)  # default selection
        mode_layout.addWidget(self.mode_radio_volumes)
        mode_layout.addWidget(self.mode_radio_chapters)
        mode_layout.addWidget(self.mode_radio_hybrid)
        self.mode_group.setLayout(mode_layout)
        layout.addWidget(self.mode_group)

        # options group with checkboxes
        self.options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        self.delete_check = QCheckBox("Delete images after conversion")
        self.debug_check = QCheckBox("Enable debug logging")
        options_layout.addWidget(self.delete_check)
        options_layout.addWidget(self.debug_check)
        self.options_group.setLayout(options_layout)
        layout.addWidget(self.options_group)

        # progress bar, initially hidden
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # read-only text area for logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # convert button to start the process
        self.convert_btn = QPushButton("Convert to PDF")
        self.convert_btn.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_btn)

        # set up logging to append to the QTextEdit widget
        self.logger_handler = QTextEditLogger(self.log_text)
        logging.getLogger("MangaPDFConverter").addHandler(self.logger_handler)

        #create menu bar
        menu_bar = self.menuBar()

        #create "Options" menu
        options_menu = menu_bar.addMenu("&options")

        #create settings action
        settings_action = QAction("settings", self)
        settings_action.setStatusTip("open settings dialog")
        settings_action.triggered.connect(self.open_settings)

        #add action to menu
        options_menu.addAction(settings_action)

    def browse_input(self):
        """
        open folder selection dialog and set selected folder path in line edit.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Manga Folder")
        if directory:
            self.input_path_edit.setText(directory)

    def start_conversion(self):
        """
        start the conversion process on a background thread with selected options.
        """
        # prevent starting multiple conversions simultaneously
        if self.converter_thread and self.converter_thread.isRunning():
            return

        path = self.input_path_edit.text()
        if not path:
            self.log_text.append("please select a manga folder.")
            return

        # determine conversion mode from selected radio button
        mode = "hybrid"
        if self.mode_radio_volumes.isChecked():
            mode = "volumes"
        elif self.mode_radio_chapters.isChecked():
            mode = "chapters"

        delete_images = self.delete_check.isChecked()
        debug = self.debug_check.isChecked()

        # show progress bar with indefinite progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        # create and start the converter thread
        self.converter_thread = ConverterThread(path, mode, delete_images, debug, settings=self.settings)
        self.converter_thread.finished.connect(self.on_conversion_finished)
        self.converter_thread.start()

    def on_conversion_finished(self):
        """
        called when the converter thread finishes; update UI accordingly.
        """
        self.progress_bar.setVisible(False)
        self.log_text.append("✅ conversion complete.")

    def open_settings(self):
        self.apply_blur_effect()
        self.settings_dialog = SettingsGUI(parent=self, current_settings=self.settings)
        self.settings_dialog.settings_saved.connect(self.on_settings_saved)
        self.settings_dialog.cancelled.connect(self.on_settings_closed)
        self.settings_dialog.finished.connect(self.on_settings_closed)
        self.settings_dialog.show()

    def on_settings_saved(self):
        self.settings = self.settings_dialog.get_settings()
        save_settings(self.settings)
        logger.info("settings saved and persisted")
        self.apply_theme()
        self.on_settings_closed()

    def on_settings_closed(self):
       self.remove_blur_effect()

    def apply_blur_effect(self):
        if hasattr(self, 'blur_effect') and self.blur_effect:
            return

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
        if hasattr(self, 'settings_dialog'):
            del self.settings_dialog



    def apply_theme(self):
        theme = self.settings.get("theme", "dark")
        stylesheet = load_stylesheet(theme)
        self.setStyleSheet(stylesheet)




