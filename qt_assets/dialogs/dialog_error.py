from utils import resource_path

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class ErrorDialog(QDialog):

    def __init__(self, error_msg):
        super().__init__()
        loadUi(resource_path('qt_assets/dialogs/Error.ui'), self)
        self.error_box.setText(error_msg)
