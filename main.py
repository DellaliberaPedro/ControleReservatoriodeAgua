import sys
from PySide6.QtWidgets import QApplication
from controller.maincontroller import MainController

def main():
    app = QApplication(sys.argv)

    window = MainController()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
