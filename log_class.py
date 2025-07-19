import logging

from PyQt5.QtCore import QObject, pyqtSignal


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