"""
Parâmetros de inicialização e comunicação em data/config.json.

- Se o arquivo não existir (os.path.exists), ele é criado com DEFAULT_CONFIG.
- Se estiver corrompido/ilegível, a aplicação NÃO quebra: usa os valores
  padrão e registra [ERROR] no log.
- Chaves que faltarem no arquivo são completadas com os valores padrão.
- A gravação é atômica: escreve num arquivo temporário e só então substitui
  o original (os.replace). Se faltar energia no meio, o config.json antigo
  continua íntegro.
"""
import copy
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

PASTA_DATA = Path(__file__).resolve().parent.parent / "data"
ARQUIVO_CONFIG = PASTA_DATA / "config.json"


class ConfigManager:
    DEFAULT_CONFIG = {
        "versao_app": "1.2.0",
        "intervalo_atualizacao_ms": 2000,
        "serial": {
            "porta": "COM3",
            "baud_rate": 115200,
            "timeout_s": 2,
        },
        "limites_iniciais": {
            "tds_max_ppm": 300.0,
            "turbidez_max_ntu": 5.0,
        },
    }

    def __init__(self, caminho=ARQUIVO_CONFIG):
        self.caminho = Path(caminho)
        self._carregar_ou_criar_padrao()
        self.dados = self.carregar()

    def _carregar_ou_criar_padrao(self) -> None:
        """Se o config.json não existir, cria a pasta e grava o DEFAULT_CONFIG."""
        if not os.path.exists(self.caminho):
            os.makedirs(self.caminho.parent, exist_ok=True)
            self.salvar(self.DEFAULT_CONFIG)
            logger.info("Arquivo %s não encontrado: criado com valores padrão.", self.caminho.name)

    def carregar(self) -> dict:
        """Lê o JSON. Em caso de erro, devolve uma cópia do padrão (fallback defensivo)."""
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, dict):
                raise ValueError("o conteúdo raiz do JSON precisa ser um objeto { }")
        except (OSError, ValueError) as erro:  # json.JSONDecodeError é subclasse de ValueError
            logger.error("Falha ao ler %s (%s). Usando configuração padrão.", self.caminho.name, erro)
            return copy.deepcopy(self.DEFAULT_CONFIG)

        logger.info("Configuração carregada de %s.", self.caminho.name)
        return self._completar_com_padrao(dados, self.DEFAULT_CONFIG)

    def salvar(self, dados: dict) -> bool:
        """Grava o dicionário formatado (indent=4) de forma atômica. Devolve True se gravou."""
        temporario = self.caminho.with_suffix(".json.tmp")
        try:
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, indent=4, ensure_ascii=False)
            os.replace(temporario, self.caminho)
        except (OSError, TypeError) as erro:
            logger.error("Falha ao salvar %s: %s", self.caminho.name, erro)
            return False
        return True

    def obter(self, secao: str, chave: str | None = None):
        """config.obter("serial", "porta") ou config.obter("intervalo_atualizacao_ms")."""
        valor = self.dados.get(secao, self.DEFAULT_CONFIG.get(secao))
        if chave is None:
            return valor
        return valor.get(chave, self.DEFAULT_CONFIG[secao][chave])

    def atualizar_serial(self, porta: str, baud_rate: int, timeout_s: int) -> bool:
        self.dados["serial"] = {"porta": porta, "baud_rate": int(baud_rate), "timeout_s": int(timeout_s)}
        salvou = self.salvar(self.dados)
        if salvou:
            logger.info("Parâmetros seriais salvos em %s: %s @ %s bps, timeout %ss.",
                        self.caminho.name, porta, baud_rate, timeout_s)
        return salvou

    @classmethod
    def _completar_com_padrao(cls, dados: dict, padrao: dict) -> dict:
        """Mescla recursiva: o que existe no arquivo vence; o que falta vem do padrão."""
        resultado = copy.deepcopy(padrao)
        for chave, valor in dados.items():
            if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
                resultado[chave] = cls._completar_com_padrao(valor, resultado[chave])
            else:
                resultado[chave] = valor
        return resultado
