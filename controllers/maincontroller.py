"""
Controller da janela principal.

Concentra a lógica: leitura simulada dos sensores, gráficos de tendência,
checagem de limite (setpoint), estado da válvula, corte emergencial e
histórico de eventos. A tela (ui/tela.ui + Ui_tela.py) não tem nenhuma
regra de negócio, só o desenho.
"""
import logging
import sqlite3
from datetime import datetime, timedelta

from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PySide6.QtCore import QDateTime, QPointF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsView, QMainWindow, QMessageBox, QVBoxLayout

from controllers.historicocontroller import HistoricoController
from controllers.settingscontroller import SettingsController
from models.config_manager import ConfigManager
from models.data_simulator import SensorSimulator
from models.evento_repository import EventoRepository
from models.regra_repository import RegraRepository
from models.sensor_data import EstadoValvula, RegistroEvento, RegraAlerta, TipoEvento
from ui.Ui_tela import Ui_MainWindow

HORAS_GRAFICO_DETALHE = 1
HORAS_GRAFICO_GERAL = 24
PROBABILIDADE_TRIP = 0.01

logger = logging.getLogger(__name__)

# severidade usada no smartgrid.log para cada tipo de evento da tabela
NIVEL_LOG_POR_TIPO = {
    TipoEvento.STATUS: logging.INFO,
    TipoEvento.COMANDO: logging.INFO,
    TipoEvento.ALERTA: logging.WARNING,
}

# sensor da regra -> (atributo da LeituraTelemetria, nome curto, unidade)
SENSORES_LEITURA = {
    "TDS (ppm)": ("tds_ppm", "TDS", "ppm"),
    "Turbidez (NTU)": ("turbidez_ntu", "Turbidez", "NTU"),
    "Temperatura (°C)": ("temperatura_c", "Temperatura", "°C"),
}


class MainController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # parametros de inicializacao/comunicacao (data/config.json)
        self.config = ConfigManager()

        self.simulador = SensorSimulator()
        self.estado_valvula = EstadoValvula.ABERTA

        # cada lista guarda o historico completo (tempo + valor) de um sensor
        self.tempos = []
        self.temperaturas = []
        self.tds_valores = []
        self.turbidez_valores = []

        # regras de alerta persistidas no SQLite (tabela regras_alerta)
        self.regras = self._carregar_regras()
        self.regras_violadas = set()  # regras (nome, sensor) estouradas na ultima leitura
        self._sincronizar_spinboxes()

        self._montar_graficos()
        self._carregar_historico_inicial()
        self._conectar_sinais()
        self._aplicar_config_serial()

        self._log_evento(TipoEvento.STATUS, "Dashboard inicializado (dados simulados).", "-")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_telemetria)
        self.timer.start(self._intervalo_atualizacao_ms())

    # ------------------------------------------------------------------
    # Regras de alerta (SQLite)
    # ------------------------------------------------------------------
    def _regras_padrao(self):
        """Regras iniciais montadas a partir de limites_iniciais do config.json."""
        limites = self.config.obter("limites_iniciais")
        try:
            tds = float(limites["tds_max_ppm"])
            turbidez = float(limites["turbidez_max_ntu"])
        except (KeyError, TypeError, ValueError):
            logger.warning("limites_iniciais inválidos no config.json; usando os valores padrão do programa.")
            padrao = ConfigManager.DEFAULT_CONFIG["limites_iniciais"]
            tds, turbidez = padrao["tds_max_ppm"], padrao["turbidez_max_ntu"]
        return [
            RegraAlerta(nome="TDS máximo", sensor="TDS (ppm)", valor_maximo=tds, ativa=True),
            RegraAlerta(nome="Turbidez máxima", sensor="Turbidez (NTU)", valor_maximo=turbidez, ativa=True),
        ]

    def _carregar_regras(self):
        try:
            regras = RegraRepository.listar_todos()
            if not regras:  # primeira execucao: banco vazio
                regras = self._regras_padrao()
                RegraRepository.substituir_todas(regras)
                logger.info("Tabela regras_alerta vazia: regras iniciais criadas a partir do config.json.")
            return regras
        except sqlite3.Error as erro:
            logger.error("Falha ao carregar as regras do SQLite: %s. Usando regras padrão em memória.", erro)
            QMessageBox.warning(self, "Banco de dados", f"Não foi possível carregar as regras salvas.\n{erro}")
            return self._regras_padrao()

    def _primeira_regra_ativa(self, sensor):
        return next((r for r in self.regras if r.sensor == sensor and r.ativa), None)

    def _sincronizar_spinboxes(self):
        """Os spinboxes do dashboard mostram (e editam) a 1a regra ativa de TDS e de Turbidez."""
        for sensor, spin in (("TDS (ppm)", self.ui.spin_limite_tds), ("Turbidez (NTU)", self.ui.spin_limite_turbidez)):
            regra = self._primeira_regra_ativa(sensor)
            spin.setEnabled(regra is not None)
            if regra is not None:
                spin.setValue(regra.valor_maximo)

    def _alterar_limite_rapido(self, sensor, spin):
        """Chamado quando o operador termina de editar um spinbox de limite no dashboard."""
        regra = self._primeira_regra_ativa(sensor)
        novo_valor = round(spin.value(), 2)
        if regra is None or abs(regra.valor_maximo - novo_valor) < 1e-9:
            return  # nada mudou

        if novo_valor <= 0:
            logger.warning("Entrada inválida bloqueada: limite de %s = %s (deve ser maior que zero).", sensor, novo_valor)
            QMessageBox.warning(self, "Entrada inválida", "O limite deve ser maior que zero.")
            spin.setValue(regra.valor_maximo)
            return

        valor_anterior = regra.valor_maximo
        regra.valor_maximo = novo_valor
        try:
            if regra.id is None or not RegraRepository.atualizar(regra):
                raise LookupError("regra não encontrada no banco")
        except (sqlite3.Error, LookupError) as erro:
            regra.valor_maximo = valor_anterior
            spin.setValue(valor_anterior)
            logger.error("Falha ao salvar o limite de %s no SQLite: %s", sensor, erro)
            QMessageBox.critical(self, "Falha ao salvar", f"O limite não foi salvo.\n{erro}")
            return

        self._log_evento(
            TipoEvento.COMANDO,
            f"Limite de {sensor} alterado de {valor_anterior:.2f} para {novo_valor:.2f}.",
            f"{novo_valor:.2f}",
        )

    def _intervalo_atualizacao_ms(self):
        try:
            intervalo = int(self.config.obter("intervalo_atualizacao_ms"))
        except (TypeError, ValueError):
            intervalo = ConfigManager.DEFAULT_CONFIG["intervalo_atualizacao_ms"]
            logger.warning("intervalo_atualizacao_ms inválido no config.json; usando %s ms.", intervalo)
        return max(200, intervalo)  # evita travar a tela com um valor absurdo

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _criar_mini_grafico(self, titulo):
        serie = QLineSeries()

        chart = QChart()
        chart.setTheme(QChart.ChartThemeDark)
        chart.setAnimationOptions(QChart.NoAnimation)
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
        # forca redesenho completo do viewport a cada atualizacao: sem isso, em alguns
        # ambientes Windows o QChartView so repinta a regiao "suja" e a linha antiga
        # some/fica parcial quando os pontos mudam rapido (a cada 2s).
        chart_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(chart_view)
        return chart_view

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

        self.view_temp = self._exibir_grafico(self.ui.chart_temperatura, self.chart_temp)
        self.view_tds = self._exibir_grafico(self.ui.chart_tds, self.chart_tds)
        self.view_turbidez = self._exibir_grafico(self.ui.chart_turbidez, self.chart_turbidez)

        # grafico geral, com os 3 sensores juntos e as 24h completas
        self.serie_geral_temperatura = QLineSeries()
        self.serie_geral_temperatura.setName("Temperatura (°C)")
        self.serie_geral_tds = QLineSeries()
        self.serie_geral_tds.setName("TDS (ppm)")
        self.serie_geral_turbidez = QLineSeries()
        self.serie_geral_turbidez.setName("Turbidez (NTU)")

        self.chart_geral = QChart()
        self.chart_geral.setTheme(QChart.ChartThemeDark)
        self.chart_geral.setAnimationOptions(QChart.NoAnimation)
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

        self.view_geral = self._exibir_grafico(self.ui.chart_geral, self.chart_geral)

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
        
        # ---> ATALHO DE TECLADO ADICIONADO AQUI <---
        self.ui.btn_emergencia.setShortcut("Space")
        
        self.ui.btn_abrir_valvula.clicked.connect(self.reabrir_valvula)
        self.ui.btn_conectar.clicked.connect(self.conectar_serial)
        self.ui.btn_desconectar.clicked.connect(self.desconectar_serial)
        self.ui.btn_abrir_configuracoes.clicked.connect(self.abrir_configuracoes)
        self.ui.btn_abrir_historico.clicked.connect(self.abrir_historico)
        self.ui.spin_limite_tds.editingFinished.connect(
            lambda: self._alterar_limite_rapido("TDS (ppm)", self.ui.spin_limite_tds)
        )
        self.ui.spin_limite_turbidez.editingFinished.connect(
            lambda: self._alterar_limite_rapido("Turbidez (NTU)", self.ui.spin_limite_turbidez)
        )

    def abrir_configuracoes(self):
        dialogo = SettingsController(self.regras, parent=self)
        if not dialogo.exec():
            return  # operador cancelou

        try:
            RegraRepository.substituir_todas(dialogo.regras)  # transacao unica: tudo ou nada
            self.regras = RegraRepository.listar_todos()
        except sqlite3.Error as erro:
            logger.error("Falha ao salvar as regras no SQLite. Rollback executado: %s", erro)
            QMessageBox.critical(
                self, "Falha ao salvar", f"As regras NÃO foram salvas (as anteriores foram mantidas).\n{erro}"
            )
            return

        self.regras_violadas.clear()
        self._sincronizar_spinboxes()
        self._log_evento(
            TipoEvento.COMANDO, f"Regras de alerta atualizadas via configuração ({len(self.regras)} regras).", "-"
        )

    def abrir_historico(self):
        dialogo = HistoricoController(parent=self)
        dialogo.exec()

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

        for view in (self.view_temp, self.view_tds, self.view_turbidez, self.view_geral):
            view.scene().invalidate(view.scene().sceneRect())
            view.viewport().repaint()

    # ------------------------------------------------------------------
    # Setpoints
    # ------------------------------------------------------------------
    def _checar_setpoints(self, leitura):
        """Compara a leitura com TODAS as regras ativas do banco (TDS, Turbidez e Temperatura)."""
        violadas_agora = set()
        for regra in self.regras:
            if not regra.ativa or regra.sensor not in SENSORES_LEITURA:
                continue
            atributo, nome, unidade = SENSORES_LEITURA[regra.sensor]
            valor = getattr(leitura, atributo)
            if valor <= regra.valor_maximo:
                continue

            chave = (regra.nome, regra.sensor)
            violadas_agora.add(chave)
            if chave not in self.regras_violadas:  # registra so quando a violacao comeca
                descricao = (
                    f"Limite de {nome} violado: {valor:.2f} {unidade} "
                    f"(limite configurado: {regra.valor_maximo:.2f} {unidade})."
                )
                self._log_evento(TipoEvento.ALERTA, descricao, f"{valor:.2f} {unidade}")
                self._aplicar_alarme_visual(True, descricao)

        if self.regras_violadas and not violadas_agora:
            self._aplicar_alarme_visual(False, "Leituras normalizadas.")
            self._log_evento(TipoEvento.STATUS, "Leituras normalizadas (todos os limites respeitados).", "-")
        self.regras_violadas = violadas_agora

    def _aplicar_alarme_visual(self, ativo, texto):
        """Dashboard fica com borda amarela enquanto algum limite estiver violado."""
        if ativo:
            self.ui.group_telemetria.setStyleSheet("QGroupBox { border: 2px solid #e0a132; }")
            self.ui.lbl_ultimo_evento.setStyleSheet("color: #e0a132; font-weight: bold;")
        else:
            self.ui.group_telemetria.setStyleSheet("")
            self.ui.lbl_ultimo_evento.setStyleSheet("")
        self.ui.lbl_ultimo_evento.setText(texto)

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
        # fechar a valvula = corte de carga -> sempre WARNING no log de auditoria
        self._log_evento(TipoEvento.ALERTA if avisar else TipoEvento.COMANDO, motivo, valor, nivel_log=logging.WARNING)
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
    def _aplicar_config_serial(self):
        """Preenche o painel serial com os valores salvos no config.json."""
        serial = self.config.obter("serial")
        for combo, valor in (
            (self.ui.combo_porta_com, str(serial["porta"])),
            (self.ui.combo_baud_rate, str(serial["baud_rate"])),
        ):
            if combo.findText(valor) < 0:  # porta/baud que nao esta na lista padrao
                combo.addItem(valor)
            combo.setCurrentText(valor)
        try:
            self.ui.spin_timeout.setValue(int(serial["timeout_s"]))
        except (TypeError, ValueError):
            logger.warning("timeout_s inválido no config.json: %r. Mantido o valor da tela.", serial["timeout_s"])

    def conectar_serial(self):
        porta = self.ui.combo_porta_com.currentText()
        baud = self.ui.combo_baud_rate.currentText()
        timeout = self.ui.spin_timeout.value()

        # a ultima configuracao usada fica salva para a proxima abertura do programa
        if not self.config.atualizar_serial(porta, baud, timeout):
            QMessageBox.warning(self, "Configuração", "Não foi possível salvar os parâmetros em config.json.")
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
    def _log_evento(self, tipo, descricao, valor, nivel_log=None):
        """Registra o evento no SQLite (tabela eventos) e no logs/smartgrid.log."""
        registro = RegistroEvento(timestamp=datetime.now(), tipo=tipo, descricao=descricao, valor_medido=valor)

        nivel = nivel_log if nivel_log is not None else NIVEL_LOG_POR_TIPO[tipo]
        logger.log(nivel, "%s: %s (valor medido: %s)", tipo.value, descricao, valor)

        try:
            EventoRepository.inserir(registro)
        except sqlite3.Error as erro:
            # o evento continua no smartgrid.log mesmo se o banco falhar
            logger.error("Falha ao gravar evento no SQLite (%s): %s", descricao, erro)
            self.statusBar().showMessage(f"ERRO: evento não gravado no banco — {erro}", 10000)
        return registro