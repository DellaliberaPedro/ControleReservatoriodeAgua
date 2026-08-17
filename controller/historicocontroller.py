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
    """
    Janela modal que exibe o histórico de eventos do sistema
    (cortes de emergência, ultrapassagem de limites, trocas de estado
    do disjuntor) em uma tabela filtrável por data.

    A lista de eventos é recebida por referência do MainController,
    então qualquer evento novo registrado lá é refletido aqui
    automaticamente através do timer de atualização periódica.
    """

    def __init__(self, eventos, parent=None):
        """
        Inicializa o diálogo de histórico.

        Args:
            eventos: lista viva de eventos (mesma referência usada pelo
                MainController — não é copiada, então mudanças externas
                aparecem aqui sem precisar recriar o diálogo).
            parent: widget pai do diálogo (padrão do Qt).
        """
        super().__init__(parent)
        self.ui = Ui_HistoricoDialog()
        self.ui.setupUi(self)
        self.eventos = eventos  # referencia a lista viva do MainController

        # ajusta as colunas da tabela: largura pelo conteúdo, exceto a
        # coluna de descrição (índice 2), que se estica para ocupar
        # o espaço restante
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
        """
        Repopula a tabela com os eventos cuja data seja igual ou
        posterior à data selecionada no filtro.

        Preserva a posição de rolagem quando o usuário tem uma linha
        selecionada; caso contrário, rola automaticamente até o final
        para mostrar o evento mais recente.
        """
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
