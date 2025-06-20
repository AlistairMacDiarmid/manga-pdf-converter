# imports
import logging
import os
import sys

from AnyQt.QtWidgets import QButtonGroup
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, \
    QLineEdit, QPushButton, QFileDialog, QGroupBox, QRadioButton, QCheckBox, QProgressBar, \
    QTextEdit, QMessageBox

from manga_pdf_converter import process_volumes, process_chapters, process_hybrid


class WorkerThread(QThread):
    """
    worker thread for processing
    this prevents GUI from freezing during long operations
    """
    # define signals
    progress_update = pyqtSignal(str)  # used for status messages
    finished_signal = pyqtSignal(bool, str)  # for completion (success, message)

    def __init__(self, path, mode, delete_images):
        super().__init__()
        self.path = path
        self.mode = mode
        self.delete_images = delete_images
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        """
        run in a separate thread
        NEVER UPDATE UI FROM HERE - USE SIGNALS!!!!
        """
        try:
            self.progress_update.emit(f"Starting conversion in {self.mode.upper()} mode")
            self.progress_update.emit(f"Source: {self.path}")
            self.progress_update.emit(f"Delete images: {'Yes' if self.delete_images else 'No'}")
            self.progress_update.emit("-" * 50)

            # function calls based on mode
            if self.mode == "volumes":
                process_volumes(self.path, self.delete_images)
            elif self.mode == "chapters":
                process_chapters(self.path, self.delete_images)
            else:  # hybrid
                process_hybrid(self.path, self.delete_images)

            if not self.is_cancelled:
                self.finished_signal.emit(True, "Conversion completed successfully!")

        except Exception as e:
            if not self.is_cancelled:
                self.finished_signal.emit(False, f"Conversion failed: {str(e)}")


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
        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        # set the window properties
        self.setWindowTitle("Manga PDF converter")
        self.setGeometry(0, 0, 475, 900)

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

        # status label (new feature)
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

    def apply_dark_theme(self):
        """apply a modern dark theme to application"""
        self.setStyleSheet("""
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
        """)

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

        radio_btn_widget.setStyleSheet("background-color: #353535;")

        # add radio button widget to groupbox
        mode_selection_section_layout.addWidget(radio_btn_widget)

        # add descriptions for each processing mode
        mode_desc_label = QLabel("☆ hybrid: groups volumes and treats other folders as individual chapters\n"
                                 "☆ volumes: groups folders by volume names (v1, v2, etc)\n"
                                 "☆ chapters: each folder becomes a separate pdf")

        mode_desc_label.setStyleSheet("background-color:#353535; font-size: 12px;")
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
        self.delete_checkbox.setStyleSheet("background-color: #353535;")
        options_group_layout.addWidget(self.delete_checkbox)

        self.warning_label = QLabel("warning: this will permanently delete the image files")
        self.warning_label.setStyleSheet("color:#d32f2f; font-size: 11px;background-color: #353535; font-weight:bold;")
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

        controls_group_layout.addStretch()

        return controls_group_box

    def create_progress_section(self):
        progress_group_box = QGroupBox("logging")
        progress_group_layout = QVBoxLayout()
        progress_group_box.setLayout(progress_group_layout)

        # progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # hide progress bar initially
        progress_group_layout.addWidget(self.progress_bar)

        # logging area
        self.log_text_area = QTextEdit()
        self.log_text_area.setMaximumHeight(250)
        self.log_text_area.setFont(QFont("Consolas", 9))
        self.log_text_area.setReadOnly(True)
        progress_group_layout.addWidget(self.log_text_area)

        # clear log button
        clear_button_layout = QHBoxLayout()
        clear_button_layout.addStretch()

        self.clear_log_button = QPushButton("Clear Log")
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

        # create and start the worker thread
        self.worker_thread = WorkerThread(self.selected_path, process_mode, delete_images)
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