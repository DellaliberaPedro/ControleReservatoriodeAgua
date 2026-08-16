from PySide6.QtWidgets import QMainWindow
from ui.Ui_tela import Ui_MainWindow


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
