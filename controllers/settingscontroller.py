"""
Controller do modal (QDialog) de configuração de regras de alerta.

Recebe a lista atual de regras, deixa o operador adicionar/remover/editar e
devolve a lista atualizada quando confirma (OK). Se cancelar, quem
chamou esse dialog simplesmente ignora o resultado.

Validação preventiva: nada inválido sai daqui. Campo vazio, texto em campo
numérico, valor negativo/zero ou sensor desconhecido -> QMessageBox.warning,
registro no log e o diálogo continua aberto para correção.
"""
import logging
from copy import deepcopy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHeaderView, QMessageBox, QTableWidgetItem

from models.sensor_data import SENSORES_VALIDOS, VALOR_MAXIMO_REGRA, RegraAlerta
from ui.Ui_tela_configuracoes import Ui_SettingsDialog

logger = logging.getLogger(__name__)

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

    # ------------------------------------------------------------------
    # Tabela
    # ------------------------------------------------------------------
    def _popular_tabela(self):
        self.ui.table_regras.setRowCount(0)
        for regra in self.regras:
            self._inserir_linha(regra)

    def _inserir_linha(self, regra):
        linha = self.ui.table_regras.rowCount()
        self.ui.table_regras.insertRow(linha)
        self.ui.table_regras.setItem(linha, COLUNA_NOME, QTableWidgetItem(regra.nome))

        # o sensor vem do combo; na tabela ele fica somente leitura
        item_sensor = QTableWidgetItem(regra.sensor)
        item_sensor.setFlags(item_sensor.flags() & ~Qt.ItemIsEditable)
        self.ui.table_regras.setItem(linha, COLUNA_SENSOR, item_sensor)

        self.ui.table_regras.setItem(linha, COLUNA_VALOR, QTableWidgetItem(f"{regra.valor_maximo:.2f}"))

        item_ativa = QTableWidgetItem()
        item_ativa.setFlags((item_ativa.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsEditable)
        item_ativa.setCheckState(Qt.Checked if regra.ativa else Qt.Unchecked)
        self.ui.table_regras.setItem(linha, COLUNA_ATIVA, item_ativa)

    # ------------------------------------------------------------------
    # Validação
    # ------------------------------------------------------------------
    @staticmethod
    def _validar_nome(texto, onde):
        nome = (texto or "").strip()
        if not nome:
            raise ValueError(f"{onde}: o nome da regra não pode ficar em branco.")
        return nome

    @staticmethod
    def _converter_valor(texto, onde):
        """Converte o texto digitado em float, aceitando vírgula. Lança ValueError com mensagem clara."""
        texto = (texto or "").strip()
        if not texto:
            raise ValueError(f"{onde}: o valor máximo não pode ficar em branco.")
        try:
            valor = float(texto.replace(",", "."))
        except ValueError:
            raise ValueError(f"{onde}: '{texto}' não é um número válido.") from None
        if valor <= 0:
            raise ValueError(f"{onde}: o valor máximo deve ser maior que zero (digitado: {valor}).")
        if valor > VALOR_MAXIMO_REGRA:
            raise ValueError(f"{onde}: o valor máximo não pode passar de {VALOR_MAXIMO_REGRA:.0f}.")
        return valor

    @staticmethod
    def _validar_sensor(texto, onde):
        if texto not in SENSORES_VALIDOS:
            raise ValueError(f"{onde}: sensor '{texto}' não é suportado.")
        return texto

    def _avisar_entrada_invalida(self, erro):
        mensagem = str(erro)
        self.ui.lbl_validacao.setText(mensagem)
        logger.warning("Entrada inválida bloqueada na janela de regras: %s", mensagem)
        QMessageBox.warning(self, "Entrada inválida", mensagem)

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def adicionar_regra(self):
        try:
            nome = self._validar_nome(self.ui.edit_nome_regra.text(), "Nova regra")
            sensor = self._validar_sensor(self.ui.combo_sensor_regra.currentText(), "Nova regra")
            valor = self._converter_valor(str(self.ui.spin_valor_regra.value()), "Nova regra")
        except ValueError as erro:
            self._avisar_entrada_invalida(erro)
            return

        nova_regra = RegraAlerta(nome=nome, sensor=sensor, valor_maximo=valor, ativa=True)
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

    def _texto_da_celula(self, linha, coluna):
        item = self.ui.table_regras.item(linha, coluna)
        return item.text() if item is not None else ""

    def _ler_regras_da_tabela(self):
        """Lê e valida todas as linhas. Lança ValueError na primeira célula inválida (e a seleciona)."""
        regras = []
        for linha in range(self.ui.table_regras.rowCount()):
            onde = f"Linha {linha + 1}"
            try:
                nome = self._validar_nome(self._texto_da_celula(linha, COLUNA_NOME), onde)
                sensor = self._validar_sensor(self._texto_da_celula(linha, COLUNA_SENSOR), onde)
                valor = self._converter_valor(self._texto_da_celula(linha, COLUNA_VALOR), onde)
            except ValueError:
                self.ui.table_regras.setCurrentCell(linha, COLUNA_VALOR)
                raise

            item_ativa = self.ui.table_regras.item(linha, COLUNA_ATIVA)
            ativa = item_ativa is not None and item_ativa.checkState() == Qt.Checked
            regras.append(RegraAlerta(nome=nome, sensor=sensor, valor_maximo=valor, ativa=ativa))
        return regras

    def validar_e_aceitar(self):
        try:
            regras = self._ler_regras_da_tabela()
        except ValueError as erro:
            self._avisar_entrada_invalida(erro)
            return

        ativas = [r for r in regras if r.ativa]
        if len(ativas) < MINIMO_REGRAS:
            self._avisar_entrada_invalida(ValueError(f"É necessário manter ao menos {MINIMO_REGRAS} regras ativas."))
            return

        self.regras = regras
        self.accept()
