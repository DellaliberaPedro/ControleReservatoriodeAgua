# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tela.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDoubleSpinBox,
    QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLCDNumber, QLabel, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1180, 860)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layout_principal = QVBoxLayout(self.centralwidget)
        self.layout_principal.setObjectName(u"layout_principal")
        self.lbl_titulo = QLabel(self.centralwidget)
        self.lbl_titulo.setObjectName(u"lbl_titulo")
        self.lbl_titulo.setAlignment(Qt.AlignCenter)
        self.lbl_titulo.setStyleSheet(u"font-size: 20px; font-weight: bold; padding: 8px;")

        self.layout_principal.addWidget(self.lbl_titulo)

        self.layout_linha_topo = QHBoxLayout()
        self.layout_linha_topo.setObjectName(u"layout_linha_topo")
        self.group_telemetria = QGroupBox(self.centralwidget)
        self.group_telemetria.setObjectName(u"group_telemetria")
        self.grid_telemetria = QGridLayout(self.group_telemetria)
        self.grid_telemetria.setObjectName(u"grid_telemetria")
        self.lbl_temperatura = QLabel(self.group_telemetria)
        self.lbl_temperatura.setObjectName(u"lbl_temperatura")

        self.grid_telemetria.addWidget(self.lbl_temperatura, 0, 0, 1, 1)

        self.lcd_temperatura = QLCDNumber(self.group_telemetria)
        self.lcd_temperatura.setObjectName(u"lcd_temperatura")
        self.lcd_temperatura.setDigitCount(5)

        self.grid_telemetria.addWidget(self.lcd_temperatura, 0, 1, 1, 1)

        self.lbl_tds = QLabel(self.group_telemetria)
        self.lbl_tds.setObjectName(u"lbl_tds")

        self.grid_telemetria.addWidget(self.lbl_tds, 1, 0, 1, 1)

        self.lcd_tds = QLCDNumber(self.group_telemetria)
        self.lcd_tds.setObjectName(u"lcd_tds")
        self.lcd_tds.setDigitCount(5)

        self.grid_telemetria.addWidget(self.lcd_tds, 1, 1, 1, 1)

        self.lbl_turbidez = QLabel(self.group_telemetria)
        self.lbl_turbidez.setObjectName(u"lbl_turbidez")

        self.grid_telemetria.addWidget(self.lbl_turbidez, 2, 0, 1, 1)

        self.lcd_turbidez = QLCDNumber(self.group_telemetria)
        self.lcd_turbidez.setObjectName(u"lcd_turbidez")
        self.lcd_turbidez.setDigitCount(5)

        self.grid_telemetria.addWidget(self.lcd_turbidez, 2, 1, 1, 1)

        self.lbl_iqa = QLabel(self.group_telemetria)
        self.lbl_iqa.setObjectName(u"lbl_iqa")
        self.lbl_iqa.setStyleSheet(u"font-weight: bold;")

        self.grid_telemetria.addWidget(self.lbl_iqa, 3, 0, 1, 1)

        self.lcd_iqa = QLCDNumber(self.group_telemetria)
        self.lcd_iqa.setObjectName(u"lcd_iqa")
        self.lcd_iqa.setDigitCount(5)

        self.grid_telemetria.addWidget(self.lcd_iqa, 3, 1, 1, 1)


        self.layout_linha_topo.addWidget(self.group_telemetria)

        self.group_estado = QGroupBox(self.centralwidget)
        self.group_estado.setObjectName(u"group_estado")
        self.layout_estado = QVBoxLayout(self.group_estado)
        self.layout_estado.setObjectName(u"layout_estado")
        self.lbl_valvula_status = QLabel(self.group_estado)
        self.lbl_valvula_status.setObjectName(u"lbl_valvula_status")
        self.lbl_valvula_status.setAlignment(Qt.AlignCenter)
        self.lbl_valvula_status.setMinimumSize(QSize(0, 48))
        self.lbl_valvula_status.setStyleSheet(u"background-color: #2ecc71; color: white; font-weight: bold; border-radius: 4px; padding: 8px;")

        self.layout_estado.addWidget(self.lbl_valvula_status)

        self.btn_emergencia = QPushButton(self.group_estado)
        self.btn_emergencia.setObjectName(u"btn_emergencia")
        self.btn_emergencia.setMinimumSize(QSize(0, 56))

        self.layout_estado.addWidget(self.btn_emergencia)

        self.lbl_ultimo_evento = QLabel(self.group_estado)
        self.lbl_ultimo_evento.setObjectName(u"lbl_ultimo_evento")
        self.lbl_ultimo_evento.setWordWrap(True)

        self.layout_estado.addWidget(self.lbl_ultimo_evento)


        self.layout_linha_topo.addWidget(self.group_estado)

        self.group_setpoints = QGroupBox(self.centralwidget)
        self.group_setpoints.setObjectName(u"group_setpoints")
        self.form_setpoints = QFormLayout(self.group_setpoints)
        self.form_setpoints.setObjectName(u"form_setpoints")
        self.lbl_limite_tds = QLabel(self.group_setpoints)
        self.lbl_limite_tds.setObjectName(u"lbl_limite_tds")

        self.form_setpoints.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lbl_limite_tds)

        self.spin_limite_tds = QDoubleSpinBox(self.group_setpoints)
        self.spin_limite_tds.setObjectName(u"spin_limite_tds")
        self.spin_limite_tds.setMaximum(1000.000000000000000)
        self.spin_limite_tds.setValue(300.000000000000000)

        self.form_setpoints.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spin_limite_tds)

        self.lbl_limite_turbidez = QLabel(self.group_setpoints)
        self.lbl_limite_turbidez.setObjectName(u"lbl_limite_turbidez")

        self.form_setpoints.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lbl_limite_turbidez)

        self.spin_limite_turbidez = QDoubleSpinBox(self.group_setpoints)
        self.spin_limite_turbidez.setObjectName(u"spin_limite_turbidez")
        self.spin_limite_turbidez.setMaximum(100.000000000000000)
        self.spin_limite_turbidez.setValue(5.000000000000000)

        self.form_setpoints.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spin_limite_turbidez)


        self.layout_linha_topo.addWidget(self.group_setpoints)


        self.layout_principal.addLayout(self.layout_linha_topo)

        self.group_grafico = QGroupBox(self.centralwidget)
        self.group_grafico.setObjectName(u"group_grafico")
        self.layout_graficos = QVBoxLayout(self.group_grafico)
        self.layout_graficos.setObjectName(u"layout_graficos")
        self.layout_graficos_detalhe = QHBoxLayout()
        self.layout_graficos_detalhe.setObjectName(u"layout_graficos_detalhe")
        self.chart_temperatura = QWidget(self.group_grafico)
        self.chart_temperatura.setObjectName(u"chart_temperatura")
        self.chart_temperatura.setMinimumSize(QSize(0, 220))

        self.layout_graficos_detalhe.addWidget(self.chart_temperatura)

        self.chart_tds = QWidget(self.group_grafico)
        self.chart_tds.setObjectName(u"chart_tds")
        self.chart_tds.setMinimumSize(QSize(0, 220))

        self.layout_graficos_detalhe.addWidget(self.chart_tds)

        self.chart_turbidez = QWidget(self.group_grafico)
        self.chart_turbidez.setObjectName(u"chart_turbidez")
        self.chart_turbidez.setMinimumSize(QSize(0, 220))

        self.layout_graficos_detalhe.addWidget(self.chart_turbidez)


        self.layout_graficos.addLayout(self.layout_graficos_detalhe)

        self.chart_geral = QWidget(self.group_grafico)
        self.chart_geral.setObjectName(u"chart_geral")
        self.chart_geral.setMinimumSize(QSize(0, 240))

        self.layout_graficos.addWidget(self.chart_geral)


        self.layout_principal.addWidget(self.group_grafico)

        self.group_historico = QGroupBox(self.centralwidget)
        self.group_historico.setObjectName(u"group_historico")
        self.layout_historico = QVBoxLayout(self.group_historico)
        self.layout_historico.setObjectName(u"layout_historico")
        self.table_historico = QTableWidget(self.group_historico)
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

        self.layout_historico.addWidget(self.table_historico)


        self.layout_principal.addWidget(self.group_historico)

        self.group_serial = QGroupBox(self.centralwidget)
        self.group_serial.setObjectName(u"group_serial")
        self.layout_serial = QHBoxLayout(self.group_serial)
        self.layout_serial.setObjectName(u"layout_serial")
        self.lbl_porta_com = QLabel(self.group_serial)
        self.lbl_porta_com.setObjectName(u"lbl_porta_com")

        self.layout_serial.addWidget(self.lbl_porta_com)

        self.combo_porta_com = QComboBox(self.group_serial)
        self.combo_porta_com.addItem("")
        self.combo_porta_com.addItem("")
        self.combo_porta_com.addItem("")
        self.combo_porta_com.setObjectName(u"combo_porta_com")

        self.layout_serial.addWidget(self.combo_porta_com)

        self.lbl_baud_rate = QLabel(self.group_serial)
        self.lbl_baud_rate.setObjectName(u"lbl_baud_rate")

        self.layout_serial.addWidget(self.lbl_baud_rate)

        self.combo_baud_rate = QComboBox(self.group_serial)
        self.combo_baud_rate.addItem("")
        self.combo_baud_rate.addItem("")
        self.combo_baud_rate.setObjectName(u"combo_baud_rate")

        self.layout_serial.addWidget(self.combo_baud_rate)

        self.btn_conectar = QPushButton(self.group_serial)
        self.btn_conectar.setObjectName(u"btn_conectar")

        self.layout_serial.addWidget(self.btn_conectar)

        self.btn_desconectar = QPushButton(self.group_serial)
        self.btn_desconectar.setObjectName(u"btn_desconectar")

        self.layout_serial.addWidget(self.btn_desconectar)

        self.lbl_status_conexao = QLabel(self.group_serial)
        self.lbl_status_conexao.setObjectName(u"lbl_status_conexao")
        self.lbl_status_conexao.setStyleSheet(u"font-weight: bold; color: #c0392b;")

        self.layout_serial.addWidget(self.lbl_status_conexao)


        self.layout_principal.addWidget(self.group_serial)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1180, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Controle de Reservat\u00f3rio de \u00c1gua", None))
        self.lbl_titulo.setText(QCoreApplication.translate("MainWindow", u"Controle de Reservat\u00f3rio de \u00c1gua \u2014 Supervis\u00e3o de Qualidade", None))
        self.group_telemetria.setTitle(QCoreApplication.translate("MainWindow", u"Telemetria", None))
        self.lbl_temperatura.setText(QCoreApplication.translate("MainWindow", u"Temperatura (\u00b0C)", None))
        self.lbl_tds.setText(QCoreApplication.translate("MainWindow", u"TDS (ppm)", None))
        self.lbl_turbidez.setText(QCoreApplication.translate("MainWindow", u"Turbidez (NTU)", None))
        self.lbl_iqa.setText(QCoreApplication.translate("MainWindow", u"IQA calculado", None))
        self.group_estado.setTitle(QCoreApplication.translate("MainWindow", u"Estado da V\u00e1lvula", None))
        self.lbl_valvula_status.setText(QCoreApplication.translate("MainWindow", u"V\u00e1lvula: ABERTA / NORMAL", None))
        self.btn_emergencia.setText(QCoreApplication.translate("MainWindow", u"CORTE EMERGENCIAL \u2014 FECHAR V\u00c1LVULA", None))
        self.lbl_ultimo_evento.setText(QCoreApplication.translate("MainWindow", u"Nenhum evento registrado ainda.", None))
        self.group_setpoints.setTitle(QCoreApplication.translate("MainWindow", u"Limites de Alerta", None))
        self.lbl_limite_tds.setText(QCoreApplication.translate("MainWindow", u"Limite TDS (ppm)", None))
        self.lbl_limite_turbidez.setText(QCoreApplication.translate("MainWindow", u"Limite Turbidez (NTU)", None))
        self.group_grafico.setTitle(QCoreApplication.translate("MainWindow", u"Tend\u00eancia", None))
        self.group_historico.setTitle(QCoreApplication.translate("MainWindow", u"Hist\u00f3rico de Eventos", None))
        ___qtablewidgetitem = self.table_historico.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Data / Hora", None))
        ___qtablewidgetitem1 = self.table_historico.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Tipo", None))
        ___qtablewidgetitem2 = self.table_historico.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Descri\u00e7\u00e3o", None))
        ___qtablewidgetitem3 = self.table_historico.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Valor Medido", None))
        self.group_serial.setTitle(QCoreApplication.translate("MainWindow", u"Comunica\u00e7\u00e3o Serial", None))
        self.lbl_porta_com.setText(QCoreApplication.translate("MainWindow", u"Porta COM:", None))
        self.combo_porta_com.setItemText(0, QCoreApplication.translate("MainWindow", u"COM1", None))
        self.combo_porta_com.setItemText(1, QCoreApplication.translate("MainWindow", u"COM3", None))
        self.combo_porta_com.setItemText(2, QCoreApplication.translate("MainWindow", u"COM5", None))

        self.lbl_baud_rate.setText(QCoreApplication.translate("MainWindow", u"Baud Rate:", None))
        self.combo_baud_rate.setItemText(0, QCoreApplication.translate("MainWindow", u"9600", None))
        self.combo_baud_rate.setItemText(1, QCoreApplication.translate("MainWindow", u"115200", None))

        self.btn_conectar.setText(QCoreApplication.translate("MainWindow", u"Conectar", None))
        self.btn_desconectar.setText(QCoreApplication.translate("MainWindow", u"Desconectar", None))
        self.lbl_status_conexao.setText(QCoreApplication.translate("MainWindow", u"Status: Desconectado", None))
    # retranslateUi

