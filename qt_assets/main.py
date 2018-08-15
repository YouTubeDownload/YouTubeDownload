from utils import resource_path

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi

from qt_assets.tabs import TABS
from qt_assets.dialogs.dialog_about import AboutDialog
from qt_assets.dialogs.dialog_error import ErrorDialog


class YouTubeDownloader(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        loadUi(resource_path('qt_assets/Main.ui'), self)
        self.init_menu()
        self.init_tabs()
        self.show()

    def init_menu(self):
        action_bindings = {
            'exit': self.close,
            'about': self.show_about
        }
        for action in self.file.actions() + self.options.actions() + self.help.actions():
            if action.objectName() in action_bindings.keys():
                action.triggered.connect(action_bindings[action.objectName()])

    def init_tabs(self):
        for tab in TABS:
            self.tab_manager.addTab(tab(main_window=self), tab.display_name)

    @staticmethod
    def show_about():
        about_diag = AboutDialog()
        about_diag.exec_()

    @staticmethod
    @pyqtSlot(str)
    def show_error(error_msg):
        error_dialog = ErrorDialog(error_msg)
        error_dialog.exec_()


def launch_app():
    import sys
    app = QApplication(sys.argv)
    ytdl = YouTubeDownloader()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch_app()
