# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tela_historico.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDateEdit,
    QDialog, QDialogButtonBox, QHBoxLayout, QHeaderView,
    QLabel, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_HistoricoDialog(object):
    def setupUi(self, HistoricoDialog):
        if not HistoricoDialog.objectName():
            HistoricoDialog.setObjectName(u"HistoricoDialog")
        HistoricoDialog.resize(720, 480)
        HistoricoDialog.setModal(True)
        self.layout_principal = QVBoxLayout(HistoricoDialog)
        self.layout_principal.setObjectName(u"layout_principal")
        self.lbl_titulo = QLabel(HistoricoDialog)
        self.lbl_titulo.setObjectName(u"lbl_titulo")
        self.lbl_titulo.setStyleSheet(u"font-weight: bold; font-size: 14px;")

        self.layout_principal.addWidget(self.lbl_titulo)

        self.layout_filtro_historico = QHBoxLayout()
        self.layout_filtro_historico.setObjectName(u"layout_filtro_historico")
        self.lbl_filtro_historico = QLabel(HistoricoDialog)
        self.lbl_filtro_historico.setObjectName(u"lbl_filtro_historico")

        self.layout_filtro_historico.addWidget(self.lbl_filtro_historico)

        self.date_filtro_historico = QDateEdit(HistoricoDialog)
        self.date_filtro_historico.setObjectName(u"date_filtro_historico")
        self.date_filtro_historico.setCalendarPopup(True)

        self.layout_filtro_historico.addWidget(self.date_filtro_historico)

        self.spacer_filtro_historico = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_filtro_historico.addItem(self.spacer_filtro_historico)


        self.layout_principal.addLayout(self.layout_filtro_historico)

        self.table_historico = QTableWidget(HistoricoDialog)
        if (self.table_historico.columnCount() < 4):
            self.table_historico.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.table_historico.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table_historico.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.table_historico.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.table_historico.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.table_historico.setObjectName(u"table_historico")
        self.table_historico.setAlternatingRowColors(True)
        self.table_historico.setColumnCount(4)
        self.table_historico.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_historico.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.layout_principal.addWidget(self.table_historico)

        self.buttonBox = QDialogButtonBox(HistoricoDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.layout_principal.addWidget(self.buttonBox)


        self.retranslateUi(HistoricoDialog)

        QMetaObject.connectSlotsByName(HistoricoDialog)
    # setupUi

    def retranslateUi(self, HistoricoDialog):
        HistoricoDialog.setWindowTitle(QCoreApplication.translate("HistoricoDialog", u"Hist\u00f3rico de Eventos", None))
        self.lbl_titulo.setText(QCoreApplication.translate("HistoricoDialog", u"Hist\u00f3rico de Eventos", None))
        self.lbl_filtro_historico.setText(QCoreApplication.translate("HistoricoDialog", u"Mostrar eventos a partir de:", None))
        self.date_filtro_historico.setDisplayFormat(QCoreApplication.translate("HistoricoDialog", u"dd/MM/yyyy", None))
        ___qtablewidgetitem = self.table_historico.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("HistoricoDialog", u"Data / Hora", None))
        ___qtablewidgetitem1 = self.table_historico.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("HistoricoDialog", u"Tipo", None))
        ___qtablewidgetitem2 = self.table_historico.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("HistoricoDialog", u"Descri\u00e7\u00e3o", None))
        ___qtablewidgetitem3 = self.table_historico.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("HistoricoDialog", u"Valor Medido", None))
    # retranslateUi

