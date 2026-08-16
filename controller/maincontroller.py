"""
Controller da janela principal.

Concentra a lógica: leitura simulada dos sensores, gráficos de tendência,
checagem de limite (setpoint), estado da válvula, corte emergencial e
histórico de eventos. A tela (ui/tela.ui + Ui_tela.py) não tem nenhuma
regra de negócio, só o desenho.
"""
from datetime import datetime, timedelta

from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PySide6.QtCore import QDate, QDateTime, QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHeaderView, QMainWindow, QMessageBox, QTableWidgetItem, QVBoxLayout

from controller.settingscontroller import SettingsController
from models.data_simulator import SensorSimulator
from models.sensor_data import EstadoValvula, RegistroEvento, RegraAlerta, TipoEvento
from ui.Ui_tela import Ui_MainWindow

INTERVALO_SIMULACAO_MS = 2000
HORAS_GRAFICO_DETALHE = 1
HORAS_GRAFICO_GERAL = 24
PROBABILIDADE_TRIP = 0.01


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.simulador = SensorSimulator()
        self.estado_valvula = EstadoValvula.ABERTA
        self.sobrecarga_ativa = False

        # cada lista guarda o historico completo (tempo + valor) de um sensor
        self.tempos = []
        self.temperaturas = []
        self.tds_valores = []
        self.turbidez_valores = []

        # historico completo de eventos (backing data da tabela, permite filtrar por data)
        self.eventos = []

        # regras padrao (as mesmas que ja estavam nos spinboxes)
        self.regras = [
            RegraAlerta(nome="TDS máximo", sensor="TDS (ppm)", valor_maximo=300.0, ativa=True),
            RegraAlerta(nome="Turbidez máxima", sensor="Turbidez (NTU)", valor_maximo=5.0, ativa=True),
        ]

        self._montar_graficos()
        self._configurar_tabela()
        self._configurar_filtro_historico()
        self._carregar_historico_inicial()
        self._conectar_sinais()

        self._log_evento(TipoEvento.STATUS, "Dashboard inicializado (dados simulados).", "-")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_telemetria)
        self.timer.start(INTERVALO_SIMULACAO_MS)

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _configurar_tabela(self):
        header = self.ui.table_historico.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

    def _configurar_filtro_historico(self):
        self.ui.date_filtro_historico.setDate(QDate.currentDate())
        self.ui.date_filtro_historico.dateChanged.connect(self._atualizar_filtro_historico)

    def _criar_mini_grafico(self, titulo):
        serie = QLineSeries()

        chart = QChart()
        chart.setTheme(QChart.ChartThemeDark)
        chart.setBackgroundBrush(QColor("#333333"))
        chart.setTitleBrush(QColor("#d4d4d4"))
        chart.setTitle(titulo)
        chart.addSeries(serie)
        chart.legend().setVisible(False)

        eixo_x = QDateTimeAxis()
        eixo_x.setFormat("HH:mm")
        eixo_x.setTickCount(6)
        eixo_y = QValueAxis()

        chart.addAxis(eixo_x, Qt.AlignBottom)
        chart.addAxis(eixo_y, Qt.AlignLeft)
        serie.attachAxis(eixo_x)
        serie.attachAxis(eixo_y)

        return chart, serie, eixo_x, eixo_y

    def _exibir_grafico(self, container, chart):
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(chart_view)

    def _montar_graficos(self):
        self.chart_temp, self.serie_temperatura, self.eixo_x_temp, self.eixo_y_temp = self._criar_mini_grafico(
            "Temperatura (°C) — última 1h"
        )
        self.chart_tds, self.serie_tds, self.eixo_x_tds, self.eixo_y_tds = self._criar_mini_grafico(
            "TDS (ppm) — última 1h"
        )
        self.chart_turbidez, self.serie_turbidez, self.eixo_x_turbidez, self.eixo_y_turbidez = (
            self._criar_mini_grafico("Turbidez (NTU) — última 1h")
        )

        self._exibir_grafico(self.ui.chart_temperatura, self.chart_temp)
        self._exibir_grafico(self.ui.chart_tds, self.chart_tds)
        self._exibir_grafico(self.ui.chart_turbidez, self.chart_turbidez)

        # grafico geral, com os 3 sensores juntos e as 24h completas
        self.serie_geral_temperatura = QLineSeries()
        self.serie_geral_temperatura.setName("Temperatura (°C)")
        self.serie_geral_tds = QLineSeries()
        self.serie_geral_tds.setName("TDS (ppm)")
        self.serie_geral_turbidez = QLineSeries()
        self.serie_geral_turbidez.setName("Turbidez (NTU)")

        self.chart_geral = QChart()
        self.chart_geral.setTheme(QChart.ChartThemeDark)
        self.chart_geral.setBackgroundBrush(QColor("#333333"))
        self.chart_geral.setTitleBrush(QColor("#d4d4d4"))
        self.chart_geral.setTitle("Visão Geral — últimas 24h")
        self.chart_geral.addSeries(self.serie_geral_temperatura)
        self.chart_geral.addSeries(self.serie_geral_tds)
        self.chart_geral.addSeries(self.serie_geral_turbidez)
        self.chart_geral.legend().setVisible(True)
        self.chart_geral.legend().setAlignment(Qt.AlignBottom)
        self.chart_geral.legend().setLabelColor(QColor("#c0c0c0"))

        self.eixo_x_geral = QDateTimeAxis()
        self.eixo_x_geral.setFormat("HH:mm")
        self.eixo_x_geral.setTickCount(6)
        self.eixo_y_geral = QValueAxis()
        self.chart_geral.addAxis(self.eixo_x_geral, Qt.AlignBottom)
        self.chart_geral.addAxis(self.eixo_y_geral, Qt.AlignLeft)
        for serie in (self.serie_geral_temperatura, self.serie_geral_tds, self.serie_geral_turbidez):
            serie.attachAxis(self.eixo_x_geral)
            serie.attachAxis(self.eixo_y_geral)

        self._exibir_grafico(self.ui.chart_geral, self.chart_geral)

    def _carregar_historico_inicial(self):
        historico = self.simulador.gerar_historico(horas=24, intervalo_min=10)
        for leitura in historico:
            self.tempos.append(leitura.timestamp)
            self.temperaturas.append(leitura.temperatura_c)
            self.tds_valores.append(leitura.tds_ppm)
            self.turbidez_valores.append(leitura.turbidez_ntu)

        self._atualizar_lcds(historico[-1])
        self._redesenhar_graficos()

    def _conectar_sinais(self):
        self.ui.btn_emergencia.clicked.connect(self.acionar_corte_emergencial)
        self.ui.btn_abrir_valvula.clicked.connect(self.reabrir_valvula)
        self.ui.btn_conectar.clicked.connect(self.conectar_serial)
        self.ui.btn_desconectar.clicked.connect(self.desconectar_serial)
        self.ui.btn_abrir_configuracoes.clicked.connect(self.abrir_configuracoes)

    def abrir_configuracoes(self):
        dialogo = SettingsController(self.regras, parent=self)
        if dialogo.exec():
            self.regras = dialogo.regras
            for regra in self.regras:
                if regra.sensor == "TDS (ppm)" and regra.ativa:
                    self.ui.spin_limite_tds.setValue(regra.valor_maximo)
                elif regra.sensor == "Turbidez (NTU)" and regra.ativa:
                    self.ui.spin_limite_turbidez.setValue(regra.valor_maximo)
            self._log_evento(TipoEvento.COMANDO, "Regras de alerta atualizadas via configuração.", "-")

    # ------------------------------------------------------------------
    # Loop de telemetria
    # ------------------------------------------------------------------
    def atualizar_telemetria(self):
        leitura = self.simulador.proxima_leitura()

        self.tempos.append(leitura.timestamp)
        self.temperaturas.append(leitura.temperatura_c)
        self.tds_valores.append(leitura.tds_ppm)
        self.turbidez_valores.append(leitura.turbidez_ntu)

        self._atualizar_lcds(leitura)
        self._redesenhar_graficos()
        self._checar_setpoints(leitura)
        self._checar_protecao_espontanea(leitura)

    def _atualizar_lcds(self, leitura):
        self.ui.lcd_temperatura.display(leitura.temperatura_c)
        self.ui.lcd_tds.display(leitura.tds_ppm)
        self.ui.lcd_turbidez.display(leitura.turbidez_ntu)
        self.ui.lcd_iqa.display(leitura.iqa)

    # ------------------------------------------------------------------
    # Graficos
    # ------------------------------------------------------------------
    def _pontos_na_janela(self, valores, horas):
        if not self.tempos:
            return []
        limite = self.tempos[-1] - timedelta(hours=horas)
        return [(t, v) for t, v in zip(self.tempos, valores) if t >= limite]

    def _atualizar_grafico_detalhe(self, serie, valores, eixo_x, eixo_y):
        pares = self._pontos_na_janela(valores, HORAS_GRAFICO_DETALHE)
        if not pares:
            return
        serie.replace([QPointF(t.timestamp() * 1000, v) for t, v in pares])
        tempos = [t for t, _ in pares]
        vals = [v for _, v in pares]
        eixo_x.setRange(
            QDateTime.fromMSecsSinceEpoch(int(tempos[0].timestamp() * 1000)),
            QDateTime.fromMSecsSinceEpoch(int(tempos[-1].timestamp() * 1000)),
        )
        eixo_y.setRange(min(vals) * 0.9, max(vals) * 1.1)

    def _redesenhar_graficos(self):
        self._atualizar_grafico_detalhe(self.serie_temperatura, self.temperaturas, self.eixo_x_temp, self.eixo_y_temp)
        self._atualizar_grafico_detalhe(self.serie_tds, self.tds_valores, self.eixo_x_tds, self.eixo_y_tds)
        self._atualizar_grafico_detalhe(
            self.serie_turbidez, self.turbidez_valores, self.eixo_x_turbidez, self.eixo_y_turbidez
        )

        pares_temp = self._pontos_na_janela(self.temperaturas, HORAS_GRAFICO_GERAL)
        pares_tds = self._pontos_na_janela(self.tds_valores, HORAS_GRAFICO_GERAL)
        pares_turbidez = self._pontos_na_janela(self.turbidez_valores, HORAS_GRAFICO_GERAL)
        if not pares_temp:
            return

        self.serie_geral_temperatura.replace([QPointF(t.timestamp() * 1000, v) for t, v in pares_temp])
        self.serie_geral_tds.replace([QPointF(t.timestamp() * 1000, v) for t, v in pares_tds])
        self.serie_geral_turbidez.replace([QPointF(t.timestamp() * 1000, v) for t, v in pares_turbidez])

        tempos = [t for t, _ in pares_temp]
        self.eixo_x_geral.setRange(
            QDateTime.fromMSecsSinceEpoch(int(tempos[0].timestamp() * 1000)),
            QDateTime.fromMSecsSinceEpoch(int(tempos[-1].timestamp() * 1000)),
        )
        maior = max(max(v for _, v in pares_tds), max(v for _, v in pares_turbidez), max(v for _, v in pares_temp))
        self.eixo_y_geral.setRange(0, maior * 1.1)

    # ------------------------------------------------------------------
    # Setpoints
    # ------------------------------------------------------------------
    def _checar_setpoints(self, leitura):
        limite_tds = self.ui.spin_limite_tds.value()
        limite_turbidez = self.ui.spin_limite_turbidez.value()
        excedeu = leitura.tds_ppm > limite_tds or leitura.turbidez_ntu > limite_turbidez

        if excedeu and not self.sobrecarga_ativa:
            self.sobrecarga_ativa = True
            self.ui.lbl_ultimo_evento.setStyleSheet("color: #e0a132; font-weight: bold;")
            self.ui.lbl_ultimo_evento.setText("Limite de TDS/Turbidez excedido.")
            self._log_evento(
                TipoEvento.ALERTA,
                "Limite de TDS/Turbidez excedido.",
                f"TDS {leitura.tds_ppm:.1f} ppm / Turbidez {leitura.turbidez_ntu:.2f} NTU",
            )
        elif not excedeu and self.sobrecarga_ativa:
            self.sobrecarga_ativa = False
            self.ui.lbl_ultimo_evento.setStyleSheet("")
            self.ui.lbl_ultimo_evento.setText("Leituras normalizadas.")
            self._log_evento(TipoEvento.STATUS, "Leituras normalizadas.", "-")

    # ------------------------------------------------------------------
    # Valvula
    # ------------------------------------------------------------------
    def _checar_protecao_espontanea(self, leitura):
        if self.estado_valvula == EstadoValvula.ABERTA and self.simulador.deveria_disparar_protecao(
            PROBABILIDADE_TRIP
        ):
            self._fechar_valvula(
                "Disparo espontâneo detectado no hardware (simulado).",
                f"TDS {leitura.tds_ppm:.1f} ppm / Turbidez {leitura.turbidez_ntu:.2f} NTU",
                avisar=True,
            )

    def _fechar_valvula(self, motivo, valor, avisar):
        self.estado_valvula = EstadoValvula.FECHADA
        self.ui.lbl_valvula_status.setText(f"Válvula: {EstadoValvula.FECHADA.value}")
        self.ui.lbl_valvula_status.setStyleSheet(
            "background-color: #c0392b; color: white; font-weight: bold; border-radius: 4px; padding: 8px;"
        )
        self.ui.lbl_ultimo_evento.setStyleSheet("")
        self.ui.lbl_ultimo_evento.setText(motivo)
        self._log_evento(TipoEvento.ALERTA if avisar else TipoEvento.COMANDO, motivo, valor)
        self._atualizar_botoes_valvula()
        if avisar:
            QMessageBox.warning(self, "Proteção Ativada", motivo)

    def acionar_corte_emergencial(self):
        resposta = QMessageBox.question(
            self,
            "Confirmar Corte Emergencial",
            "Tem certeza que deseja fechar a válvula de entrada imediatamente?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            self._fechar_valvula("Corte de emergência acionado via software.", "-", avisar=False)

    def reabrir_valvula(self):
        resposta = QMessageBox.question(
            self,
            "Confirmar Reabertura",
            "Confirma a reabertura da válvula de entrada?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resposta != QMessageBox.Yes:
            return
        self.estado_valvula = EstadoValvula.ABERTA
        self.ui.lbl_valvula_status.setText(f"Válvula: {EstadoValvula.ABERTA.value}")
        self.ui.lbl_valvula_status.setStyleSheet(
            "background-color: #2ecc71; color: white; font-weight: bold; border-radius: 4px; padding: 8px;"
        )
        self.ui.lbl_ultimo_evento.setStyleSheet("")
        self.ui.lbl_ultimo_evento.setText("Válvula reaberta manualmente.")
        self._log_evento(TipoEvento.COMANDO, "Válvula reaberta manualmente via software.", "-")
        self._atualizar_botoes_valvula()

    def _atualizar_botoes_valvula(self):
        aberta = self.estado_valvula == EstadoValvula.ABERTA
        self.ui.btn_emergencia.setEnabled(aberta)
        self.ui.btn_abrir_valvula.setEnabled(not aberta)

    # ------------------------------------------------------------------
    # Painel serial (visual, sem conexao real ainda)
    # ------------------------------------------------------------------
    def conectar_serial(self):
        porta = self.ui.combo_porta_com.currentText()
        baud = self.ui.combo_baud_rate.currentText()
        timeout = self.ui.spin_timeout.value()
        self.ui.lbl_status_conexao.setText(f"Status: Conectado ({porta} @ {baud}, timeout {timeout}s)")
        self.ui.lbl_status_conexao.setStyleSheet("font-weight: bold; color: #27ae60;")
        self._log_evento(
            TipoEvento.STATUS,
            f"Conexão serial estabelecida (visual) — {porta}.",
            f"{baud} bps, timeout {timeout}s",
        )

    def desconectar_serial(self):
        self.ui.lbl_status_conexao.setText("Status: Desconectado")
        self.ui.lbl_status_conexao.setStyleSheet("font-weight: bold; color: #c0392b;")
        self._log_evento(TipoEvento.STATUS, "Conexão serial encerrada (visual).", "-")

    # ------------------------------------------------------------------
    # Historico
    # ------------------------------------------------------------------
    def _log_evento(self, tipo, descricao, valor):
        registro = RegistroEvento(timestamp=datetime.now(), tipo=tipo, descricao=descricao, valor_medido=valor)
        self.eventos.append(registro)
        if registro.timestamp.date() >= self.ui.date_filtro_historico.date().toPython():
            self._inserir_linha_historico(registro)

    def _inserir_linha_historico(self, registro):
        linha = self.ui.table_historico.rowCount()
        self.ui.table_historico.insertRow(linha)
        for coluna, texto in enumerate(registro.como_linha()):
            self.ui.table_historico.setItem(linha, coluna, QTableWidgetItem(texto))
        self.ui.table_historico.scrollToBottom()

    def _atualizar_filtro_historico(self):
        data_filtro = self.ui.date_filtro_historico.date().toPython()
        self.ui.table_historico.setRowCount(0)
        for registro in self.eventos:
            if registro.timestamp.date() >= data_filtro:
                self._inserir_linha_historico(registro)
