import os

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton, QGroupBox, QLabel, QLineEdit, \
    QCheckBox, QButtonGroup, QRadioButton, QFileDialog, QMessageBox, QDialog

from utils.styles import load_stylesheet
from utils.settings import load_settings, save_settings


class SettingsGUI(QDialog):

    finished = pyqtSignal()
    settings_saved = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.parent = parent
        self.current_settings = load_settings() if current_settings is None else current_settings
        self.init_ui()
        self.apply_theme()
        self.load_settings()
        self._settings_saved = False



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


        quality_desc = QLabel("higher values = better quality but larger file size")
        quality_desc.setStyleSheet(f"font-size: 11px;")

        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_input)
        quality_layout.addWidget(quality_desc)
        layout.addWidget(quality_group)

        #PDF options
        options_group = QGroupBox("PDF Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)

        self.compression_checkbox = QCheckBox("Enable PDF compression")
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
        process_desc.setStyleSheet(f"font-size: 12px; margin-bottom: 10px;")
        processing_layout.addWidget(process_desc)

        self.format_group = QButtonGroup()

        self.keep_original_radio = QRadioButton("keep original format (fastest)")
        self.jpeg_radio = QRadioButton("convert to JPEG (smaller PDF size)")
        self.png_radio = QRadioButton("convert to PNG (preserve transparency)")

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
        res_desc.setStyleSheet(f"font-size: 12px; margin-bottom: 10px;")
        resolution_layout.addWidget(res_desc)

        self.resize_checkbox = QCheckBox("enable image resizing")
        resolution_layout.addWidget(self.resize_checkbox)

        size_layout = QHBoxLayout()

        width_label = QLabel("max width:")
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("1920")
        self.width_input.setEnabled(False)

        height_label = QLabel("max height:")
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
        self.backup_checkbox = QCheckBox("create backup of original images before conversion")
        self.delete_checkbox = QCheckBox("delete source images after successful conversion")

        delete_warning = QLabel("⚠️ warning: deletion cannot be undone!")
        delete_warning.setStyleSheet(f"font-size: 12px; font-weight: bold;color:#d32f2f;")

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
        self.light_theme_radio = QRadioButton("light")

        self.theme_group.addButton(self.dark_theme_radio)
        self.theme_group.addButton(self.light_theme_radio)

        appearance_layout.addWidget(self.dark_theme_radio)
        appearance_layout.addWidget(self.light_theme_radio)

        layout.addWidget(appearance_group)
        layout.addStretch()

        return tab


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


        save_settings(self.current_settings)

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

    def apply_theme(self):
        theme = self.current_settings.get("theme", "dark")
        stylesheet = load_stylesheet(theme)
        if not stylesheet:
            print(f"warning: empty stylesheet for theme '{theme}', skipping apply.")
            return
        try:
            self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"error applying stylesheet: {e}")