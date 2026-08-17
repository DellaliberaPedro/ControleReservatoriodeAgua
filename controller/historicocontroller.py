"""
Controller da tela (QDialog) de Histórico de Eventos.

Recebe a lista viva de eventos do MainController (mesma referência de
lista, não uma cópia) e mostra numa tabela filtrável por data. Enquanto
a janela estiver aberta, um timer interno reconsulta essa lista a cada
poucos segundos para refletir eventos novos em tempo real.
"""
from PySide6.QtCore import QDate, QTimer
from PySide6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem

from ui.Ui_tela_historico import Ui_HistoricoDialog

INTERVALO_ATUALIZACAO_MS = 2000


class HistoricoController(QDialog):
    def __init__(self, eventos, parent=None):
        super().__init__(parent)
        self.ui = Ui_HistoricoDialog()
        self.ui.setupUi(self)

        self.eventos = eventos  # referencia a lista viva do MainController

        header = self.ui.table_historico.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.ui.date_filtro_historico.setDate(QDate.currentDate())
        self.ui.date_filtro_historico.dateChanged.connect(self._atualizar_tabela)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.buttonBox.accepted.connect(self.accept)

        self._atualizar_tabela()

        # atualiza sozinho enquanto a janela estiver aberta, pra acompanhar
        # eventos novos sem precisar fechar e abrir de novo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._atualizar_tabela)
        self.timer.start(INTERVALO_ATUALIZACAO_MS)

    def _atualizar_tabela(self):
        data_filtro = self.ui.date_filtro_historico.date().toPython()
        linha_selecionada = self.ui.table_historico.currentRow()

        self.ui.table_historico.setRowCount(0)
        for registro in self.eventos:
            if registro.timestamp.date() >= data_filtro:
                linha = self.ui.table_historico.rowCount()
                self.ui.table_historico.insertRow(linha)
                for coluna, texto in enumerate(registro.como_linha()):
                    self.ui.table_historico.setItem(linha, coluna, QTableWidgetItem(texto))

        if linha_selecionada < 0:
            self.ui.table_historico.scrollToBottom()
