import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from controllers.maincontroller import MainController
from models.logger import configurar_logging

PASTA_RESOURCES = Path(__file__).resolve().parent / "resources"


def main():
    configurar_logging()
    logger = logging.getLogger("main")
    logger.info("Aplicação iniciada.")

    app = QApplication(sys.argv)

    caminho_estilo = PASTA_RESOURCES / "style.qss"
    if caminho_estilo.exists():
        app.setStyleSheet(caminho_estilo.read_text(encoding="utf-8"))

    window = MainController()
    window.show()

    codigo_saida = app.exec()
    logger.info("Aplicação encerrada (código de saída %s).", codigo_saida)
    sys.exit(codigo_saida)


if __name__ == "__main__":
    main()
