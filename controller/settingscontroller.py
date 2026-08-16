"""
Controller do modal (QDialog) de configuração de regras de alerta.

Recebe a lista atual de regras, deixa o operador adicionar/remover e
devolve a lista atualizada quando confirma (OK). Se cancelar, quem
chamou esse dialog simplesmente ignora o resultado.
"""
from copy import deepcopy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHeaderView, QMessageBox, QTableWidgetItem

from models.sensor_data import RegraAlerta
from ui.Ui_tela_configuracoes import Ui_SettingsDialog

COLUNA_NOME, COLUNA_SENSOR, COLUNA_VALOR, COLUNA_ATIVA = range(4)
MINIMO_REGRAS = 2


class SettingsController(QDialog):
    def __init__(self, regras_atuais, parent=None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        header = self.ui.table_regras.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(COLUNA_NOME, QHeaderView.Stretch)

        self.regras = deepcopy(regras_atuais)
        self._popular_tabela()

        self.ui.btn_adicionar_regra.clicked.connect(self.adicionar_regra)
        self.ui.btn_remover_regra.clicked.connect(self.remover_regra_selecionada)
        self.ui.buttonBox.accepted.connect(self.validar_e_aceitar)
        self.ui.buttonBox.rejected.connect(self.reject)

    def _popular_tabela(self):
        self.ui.table_regras.setRowCount(0)
        for regra in self.regras:
            self._inserir_linha(regra)

    def _inserir_linha(self, regra):
        linha = self.ui.table_regras.rowCount()
        self.ui.table_regras.insertRow(linha)
        self.ui.table_regras.setItem(linha, COLUNA_NOME, QTableWidgetItem(regra.nome))
        self.ui.table_regras.setItem(linha, COLUNA_SENSOR, QTableWidgetItem(regra.sensor))
        self.ui.table_regras.setItem(linha, COLUNA_VALOR, QTableWidgetItem(f"{regra.valor_maximo:.2f}"))

        item_ativa = QTableWidgetItem()
        item_ativa.setFlags(item_ativa.flags() | Qt.ItemIsUserCheckable)
        item_ativa.setCheckState(Qt.Checked if regra.ativa else Qt.Unchecked)
        self.ui.table_regras.setItem(linha, COLUNA_ATIVA, item_ativa)

    def adicionar_regra(self):
        nome = self.ui.edit_nome_regra.text().strip()
        if not nome:
            self.ui.lbl_validacao.setText("Informe um nome para a regra.")
            return

        nova_regra = RegraAlerta(
            nome=nome,
            sensor=self.ui.combo_sensor_regra.currentText(),
            valor_maximo=self.ui.spin_valor_regra.value(),
            ativa=True,
        )
        self.regras.append(nova_regra)
        self._inserir_linha(nova_regra)
        self.ui.edit_nome_regra.clear()
        self.ui.lbl_validacao.setText("")

    def remover_regra_selecionada(self):
        linha = self.ui.table_regras.currentRow()
        if linha < 0:
            self.ui.lbl_validacao.setText("Selecione uma regra para remover.")
            return
        self.ui.table_regras.removeRow(linha)
        del self.regras[linha]

    def _ler_regras_da_tabela(self):
        regras = []
        for linha in range(self.ui.table_regras.rowCount()):
            nome = self.ui.table_regras.item(linha, COLUNA_NOME).text()
            sensor = self.ui.table_regras.item(linha, COLUNA_SENSOR).text()
            valor = float(self.ui.table_regras.item(linha, COLUNA_VALOR).text())
            ativa = self.ui.table_regras.item(linha, COLUNA_ATIVA).checkState() == Qt.Checked
            regras.append(RegraAlerta(nome=nome, sensor=sensor, valor_maximo=valor, ativa=ativa))
        return regras

    def validar_e_aceitar(self):
        regras = self._ler_regras_da_tabela()
        ativas = [r for r in regras if r.ativa]

        if len(ativas) < MINIMO_REGRAS:
            self.ui.lbl_validacao.setText(f"É necessário manter ao menos {MINIMO_REGRAS} regras ativas.")
            QMessageBox.warning(
                self, "Configuração inválida", f"É necessário manter ao menos {MINIMO_REGRAS} regras ativas."
            )
            return

        self.regras = regras
        self.accept()
