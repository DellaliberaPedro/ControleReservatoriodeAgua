"""
Controller da tela (QDialog) de Histórico de Eventos.

Os dados vêm direto do SQLite (tabela eventos) via EventoRepository.listar_todos():
  - no showEvent (toda vez que a janela é exibida);
  - a cada poucos segundos enquanto ela estiver aberta, para mostrar em
    tempo real os eventos que o MainController acabou de gravar.
"""
import logging
import sqlite3

from PySide6.QtCore import QDate, QTimer
from PySide6.QtWidgets import QDialog, QHeaderView, QMessageBox, QTableWidgetItem

from models.evento_repository import EventoRepository
from ui.Ui_tela_historico import Ui_HistoricoDialog

logger = logging.getLogger(__name__)

INTERVALO_ATUALIZACAO_MS = 2000


class HistoricoController(QDialog):
    """
    Janela modal que exibe o histórico de eventos do sistema
    (cortes de emergência, ultrapassagem de limites, trocas de estado
    da válvula) em uma tabela filtrável por data.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_HistoricoDialog()
        self.ui.setupUi(self)

        # largura pelo conteúdo, exceto a coluna de descrição (índice 2), que estica
        header = self.ui.table_historico.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.ui.date_filtro_historico.setDate(QDate.currentDate())
        self.ui.date_filtro_historico.dateChanged.connect(self._atualizar_tabela)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.buttonBox.accepted.connect(self.accept)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._atualizar_tabela)

    def showEvent(self, event):
        """Carrega os eventos do banco sempre que a janela aparece e liga a atualização automática."""
        super().showEvent(event)
        self._atualizar_tabela()
        self.timer.start(INTERVALO_ATUALIZACAO_MS)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def _atualizar_tabela(self):
        """
        Repopula a tabela com os eventos do banco cuja data seja igual ou
        posterior à data do filtro. Mantém a rolagem se houver linha
        selecionada; senão, rola até o evento mais recente.
        """
        try:
            eventos = EventoRepository.listar_todos()
        except sqlite3.Error as erro:
            self.timer.stop()  # evita uma caixa de erro a cada 2 s
            logger.error("Falha ao carregar o histórico do SQLite: %s", erro)
            QMessageBox.critical(self, "Banco de dados", f"Não foi possível carregar o histórico.\n{erro}")
            return

        data_filtro = self.ui.date_filtro_historico.date().toPython()
        linha_selecionada = self.ui.table_historico.currentRow()

        self.ui.table_historico.setRowCount(0)
        for registro in eventos:
            if registro.timestamp.date() >= data_filtro:
                linha = self.ui.table_historico.rowCount()
                self.ui.table_historico.insertRow(linha)
                for coluna, texto in enumerate(registro.como_linha()):
                    self.ui.table_historico.setItem(linha, coluna, QTableWidgetItem(texto))

        if linha_selecionada < 0:
            self.ui.table_historico.scrollToBottom()
