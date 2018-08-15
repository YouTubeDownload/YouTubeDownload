from utils import resource_path

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class EncoderTab(QWidget):

    display_name = 'Encoder'

    def __init__(self):
        super().__init__()
        loadUi(resource_path('qt_assets/tabs/tab_not_yet.ui'), self)
        self.show()
