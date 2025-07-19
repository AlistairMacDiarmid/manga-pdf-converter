import os.path
import sys
import logging

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    #set up top-level logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.getLogger("PIL").setLevel(logging.WARNING)

    app = QApplication(sys.argv)

    #icon path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "resources", "icon.png")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
