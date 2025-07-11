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
    window = MainWindow()
    window.show()
    window.setWindowIcon(QIcon("icon.png"))
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
