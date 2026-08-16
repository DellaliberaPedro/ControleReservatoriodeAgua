# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tela_configuracoes.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(560, 420)
        SettingsDialog.setModal(True)
        self.layout_principal = QVBoxLayout(SettingsDialog)
        self.layout_principal.setObjectName(u"layout_principal")
        self.lbl_titulo = QLabel(SettingsDialog)
        self.lbl_titulo.setObjectName(u"lbl_titulo")
        self.lbl_titulo.setStyleSheet(u"font-weight: bold; font-size: 14px;")

        self.layout_principal.addWidget(self.lbl_titulo)

        self.table_regras = QTableWidget(SettingsDialog)
        if (self.table_regras.columnCount() < 4):
            self.table_regras.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.table_regras.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table_regras.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.table_regras.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.table_regras.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.table_regras.setObjectName(u"table_regras")
        self.table_regras.setAlternatingRowColors(True)
        self.table_regras.setColumnCount(4)

        self.layout_principal.addWidget(self.table_regras)

        self.layout_nova_regra = QHBoxLayout()
        self.layout_nova_regra.setObjectName(u"layout_nova_regra")
        self.edit_nome_regra = QLineEdit(SettingsDialog)
        self.edit_nome_regra.setObjectName(u"edit_nome_regra")
        self.edit_nome_regra.setMinimumSize(QSize(160, 0))

        self.layout_nova_regra.addWidget(self.edit_nome_regra)

        self.combo_sensor_regra = QComboBox(SettingsDialog)
        self.combo_sensor_regra.addItem("")
        self.combo_sensor_regra.addItem("")
        self.combo_sensor_regra.addItem("")
        self.combo_sensor_regra.setObjectName(u"combo_sensor_regra")

        self.layout_nova_regra.addWidget(self.combo_sensor_regra)

        self.spin_valor_regra = QDoubleSpinBox(SettingsDialog)
        self.spin_valor_regra.setObjectName(u"spin_valor_regra")
        self.spin_valor_regra.setMaximum(1000.000000000000000)

        self.layout_nova_regra.addWidget(self.spin_valor_regra)

        self.btn_adicionar_regra = QPushButton(SettingsDialog)
        self.btn_adicionar_regra.setObjectName(u"btn_adicionar_regra")

        self.layout_nova_regra.addWidget(self.btn_adicionar_regra)

        self.btn_remover_regra = QPushButton(SettingsDialog)
        self.btn_remover_regra.setObjectName(u"btn_remover_regra")

        self.layout_nova_regra.addWidget(self.btn_remover_regra)


        self.layout_principal.addLayout(self.layout_nova_regra)

        self.lbl_validacao = QLabel(SettingsDialog)
        self.lbl_validacao.setObjectName(u"lbl_validacao")
        self.lbl_validacao.setStyleSheet(u"color: #e74c3c; font-weight: bold;")

        self.layout_principal.addWidget(self.lbl_validacao)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.layout_principal.addWidget(self.buttonBox)


        self.retranslateUi(SettingsDialog)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Configura\u00e7\u00e3o de Limites", None))
        self.lbl_titulo.setText(QCoreApplication.translate("SettingsDialog", u"Regras de Alerta (m\u00ednimo de 2 regras ativas)", None))
        ___qtablewidgetitem = self.table_regras.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("SettingsDialog", u"Nome da Regra", None))
        ___qtablewidgetitem1 = self.table_regras.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("SettingsDialog", u"Sensor", None))
        ___qtablewidgetitem2 = self.table_regras.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("SettingsDialog", u"Valor M\u00e1ximo", None))
        ___qtablewidgetitem3 = self.table_regras.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("SettingsDialog", u"Ativa", None))
        self.edit_nome_regra.setPlaceholderText(QCoreApplication.translate("SettingsDialog", u"Nome da regra", None))
        self.combo_sensor_regra.setItemText(0, QCoreApplication.translate("SettingsDialog", u"TDS (ppm)", None))
        self.combo_sensor_regra.setItemText(1, QCoreApplication.translate("SettingsDialog", u"Turbidez (NTU)", None))
        self.combo_sensor_regra.setItemText(2, QCoreApplication.translate("SettingsDialog", u"Temperatura (\u00b0C)", None))

        self.btn_adicionar_regra.setText(QCoreApplication.translate("SettingsDialog", u"Adicionar", None))
        self.btn_remover_regra.setText(QCoreApplication.translate("SettingsDialog", u"Remover Selecionada", None))
        self.lbl_validacao.setText("")
    # retranslateUi

