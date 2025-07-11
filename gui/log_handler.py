import logging
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG


class QTextEditLogger(logging.Handler):
    """
    logging.Handler subclass that sends log messages to a QTextEdit widget in a thread-safe way.
    """

    def __init__(self, text_edit: QTextEdit):
        """
        initialize the handler with the target QTextEdit widget.

        Args:
            text_edit (QTextEdit): the widget to append log messages to.
        """
        super().__init__()
        self.widget = text_edit

    def emit(self, record):
        """
        format the log record and append it to the QTextEdit widget asynchronously.

        Args:
            record (logging.LogRecord): the log record to handle.
        """
        msg = self.format(record)
        # invoke append method on the QTextEdit in the GUI thread using queued connection
        QMetaObject.invokeMethod(
            self.widget,
            "append",
            Qt.QueuedConnection,
            Q_ARG(str, msg)
        )
