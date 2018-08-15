from utils import resource_path

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class AboutDialog(QDialog):

    def __init__(self):
        super().__init__()
        loadUi(resource_path('qt_assets/dialogs/About.ui'), self)

    def show_dialog(self):
        self.show()
        self.exec_()
