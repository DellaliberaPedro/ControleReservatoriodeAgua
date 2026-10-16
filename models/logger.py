"""
Subsistema de logs (diagnóstico e auditoria) -> logs/smartgrid.log

Usa o módulo nativo `logging`. A configuração é feita UMA vez, no início do
main.py, chamando configurar_logging(). Depois disso, qualquer arquivo do
projeto só precisa de:

    import logging
    logger = logging.getLogger(__name__)

    logger.info("...")      -> [INFO]     operação normal
    logger.warning("...")   -> [WARNING]  anomalia / limite violado / corte de carga
    logger.error("...")     -> [ERROR]    falha de execução, rollback, banco indisponível

Formato de cada linha do arquivo:
    15/10/2026 20:30:15 [WARNING] controllers.maincontroller: Limite de TDS violado: ...
"""
import logging
import os
import sys
from pathlib import Path

PASTA_LOGS = Path(__file__).resolve().parent.parent / "logs"
ARQUIVO_LOG = PASTA_LOGS / "smartgrid.log"

FORMATO_LINHA = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
FORMATO_DATA = "%d/%m/%Y %H:%M:%S"


def configurar_logging(nivel: int = logging.INFO) -> None:
    """Liga a gravação em logs/smartgrid.log (modo append) e também no terminal."""
    # a pasta logs/ pode não existir num clone novo -> cria antes de abrir o arquivo
    os.makedirs(PASTA_LOGS, exist_ok=True)

    logging.basicConfig(
        level=nivel,
        format=FORMATO_LINHA,
        datefmt=FORMATO_DATA,
        handlers=[
            logging.FileHandler(ARQUIVO_LOG, mode="a", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # qualquer exceção que escapar sem tratamento (inclusive dentro de um slot
    # do Qt) também vai parar no log como [ERROR], com o traceback completo
    sys.excepthook = _registrar_excecao_nao_tratada


def _registrar_excecao_nao_tratada(tipo, valor, traceback):
    if issubclass(tipo, KeyboardInterrupt):
        sys.__excepthook__(tipo, valor, traceback)
        return
    logging.getLogger("app").error(
        "Erro de execução não tratado: %s", valor, exc_info=(tipo, valor, traceback)
    )
