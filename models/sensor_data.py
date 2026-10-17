"""
Estruturas de dados do domínio (telemetria, eventos).

Nenhuma classe daqui depende de PySide6: são só dados, fáceis de testar
isoladamente e, no futuro, trocar pela leitura real vinda do STM32.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# sensores que podem receber regra de alerta (mesmos textos do combo da tela de regras)
SENSORES_VALIDOS = ("TDS (ppm)", "Turbidez (NTU)", "Temperatura (°C)")

# faixa aceita para o valor maximo de uma regra (bate com o QDoubleSpinBox da tela)
VALOR_MAXIMO_REGRA = 1000.0


class TipoEvento(str, Enum):
    COMANDO = "Comando"
    ALERTA = "Alerta"
    STATUS = "Status"


class EstadoValvula(str, Enum):
    """Texto mostrado na tela para o estado da valvula."""
    ABERTA = "ABERTA / NORMAL"
    FECHADA = "FECHADA / PROTEÇÃO ATIVADA"


class StatusDispositivo(str, Enum):
    """Valor gravado na coluna dispositivos.status (CHECK status IN ('ABERTO', 'FECHADO'))."""
    ABERTO = "ABERTO"
    FECHADO = "FECHADO"


@dataclass
class Dispositivo:
    """Atuador fisico do reservatorio (tabela dispositivos)."""
    tag: str  # identificador unico, ex.: "VALV-01"
    tipo: str  # "VALVULA" ou "RELE"
    descricao: str
    status: StatusDispositivo
    ultima_atualizacao: datetime | None = None
    id: int | None = None


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
    id: int | None = None


@dataclass
class RegistroEvento:
    timestamp: datetime
    tipo: TipoEvento
    descricao: str
    valor_medido: str = "-"
    dispositivo_id: int | None = None  # FK opcional para dispositivos.id
    id: int | None = None

    def como_linha(self) -> list[str]:
        return [
            self.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            self.tipo.value,
            self.descricao,
            self.valor_medido,
        ]
