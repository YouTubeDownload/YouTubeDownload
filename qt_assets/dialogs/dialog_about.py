from utils import resource_path

from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap


class AboutDialog(QDialog):

    def __init__(self):
        super().__init__()
        loadUi(resource_path('qt_assets/dialogs/About.ui'), self)
        self.logo_pixmap = QPixmap()
        self.logo_pixmap.load(resource_path('assets/ytdl.png'))
        self.logo.setPixmap(self.logo_pixmap)

    def show_dialog(self):
        self.show()
        self.exec_()
