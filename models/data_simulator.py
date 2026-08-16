"""
Gera leituras falsas de sensores (passeio aleatório) e um histórico
inicial pra já ter dado no gráfico assim que a tela abre.
"""
import random
from datetime import datetime, timedelta

from models.sensor_data import LeituraTelemetria

TEMPERATURA_MIN, TEMPERATURA_MAX = 15.0, 32.0
TDS_MIN, TDS_MAX = 50.0, 500.0
TURBIDEZ_MIN, TURBIDEZ_MAX = 0.0, 20.0


def calcular_iqa(tds_ppm: float, turbidez_ntu: float) -> float:
    """Indice de Qualidade da Agua (0-100), calculado a partir do TDS e da turbidez."""
    penalidade_tds = min(tds_ppm / 5.0, 60.0)
    penalidade_turbidez = min(turbidez_ntu * 2.0, 40.0)
    iqa = 100.0 - penalidade_tds - penalidade_turbidez
    return max(0.0, round(iqa, 1))


class SensorSimulator:
    def __init__(self):
        self._temperatura = 24.0
        self._tds = 180.0
        self._turbidez = 3.0

    def _passeio(self, valor, minimo, maximo, passo):
        novo_valor = valor + random.uniform(-passo, passo)
        return max(minimo, min(maximo, novo_valor))

    def proxima_leitura(self, timestamp=None) -> LeituraTelemetria:
        self._temperatura = self._passeio(self._temperatura, TEMPERATURA_MIN, TEMPERATURA_MAX, 0.3)
        self._tds = self._passeio(self._tds, TDS_MIN, TDS_MAX, 8.0)
        self._turbidez = self._passeio(self._turbidez, TURBIDEZ_MIN, TURBIDEZ_MAX, 0.6)

        return LeituraTelemetria(
            timestamp=timestamp or datetime.now(),
            temperatura_c=round(self._temperatura, 1),
            tds_ppm=round(self._tds, 1),
            turbidez_ntu=round(self._turbidez, 2),
            iqa=calcular_iqa(self._tds, self._turbidez),
        )

    def gerar_historico(self, horas=24, intervalo_min=10):
        agora = datetime.now()
        amostras = (horas * 60) // intervalo_min
        inicio = agora - timedelta(hours=horas)

        historico = []
        for i in range(amostras + 1):
            momento = inicio + timedelta(minutes=i * intervalo_min)
            historico.append(self.proxima_leitura(timestamp=momento))
        return historico

    def deveria_disparar_protecao(self, probabilidade=0.01) -> bool:
        return random.random() < probabilidade
