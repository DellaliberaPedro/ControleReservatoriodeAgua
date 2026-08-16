"""
Estruturas de dados do domínio (telemetria, eventos).

Nenhuma classe daqui depende de PySide6: são só dados, fáceis de testar
isoladamente e, no futuro, trocar pela leitura real vinda do STM32.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TipoEvento(str, Enum):
    COMANDO = "Comando"
    ALERTA = "Alerta"
    STATUS = "Status"


class EstadoValvula(str, Enum):
    ABERTA = "ABERTA / NORMAL"
    FECHADA = "FECHADA / PROTEÇÃO ATIVADA"


@dataclass
class LeituraTelemetria:
    timestamp: datetime
    temperatura_c: float
    tds_ppm: float
    turbidez_ntu: float
    iqa: float  # indice de qualidade da agua, calculado a partir do TDS e turbidez


@dataclass
class RegraAlerta:
    """Regra de limite configuravel pelo operador (setpoint)."""
    nome: str
    sensor: str  # "TDS (ppm)" ou "Turbidez (NTU)"
    valor_maximo: float
    ativa: bool = True


@dataclass
class RegistroEvento:
    timestamp: datetime
    tipo: TipoEvento
    descricao: str
    valor_medido: str

    def como_linha(self) -> list[str]:
        return [
            self.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            self.tipo.value,
            self.descricao,
            self.valor_medido,
        ]
