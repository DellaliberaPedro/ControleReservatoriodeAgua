import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from controller.maincontroller import MainController

PASTA_RESOURCES = Path(__file__).resolve().parent / "resources"


def main():
    app = QApplication(sys.argv)

    caminho_estilo = PASTA_RESOURCES / "style.qss"
    if caminho_estilo.exists():
        app.setStyleSheet(caminho_estilo.read_text(encoding="utf-8"))

    window = MainController()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
