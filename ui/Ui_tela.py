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
from PySide6.QtWidgets import (QApplication, QGridLayout, QGroupBox, QLCDNumber,
    QLabel, QMainWindow, QMenuBar, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layout_principal = QVBoxLayout(self.centralwidget)
        self.layout_principal.setObjectName(u"layout_principal")
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


        self.layout_principal.addWidget(self.group_telemetria)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Controle de Reservat\u00f3rio de \u00c1gua", None))
        self.group_telemetria.setTitle(QCoreApplication.translate("MainWindow", u"Telemetria", None))
        self.lbl_temperatura.setText(QCoreApplication.translate("MainWindow", u"Temperatura (\u00b0C)", None))
        self.lbl_tds.setText(QCoreApplication.translate("MainWindow", u"TDS (ppm)", None))
        self.lbl_turbidez.setText(QCoreApplication.translate("MainWindow", u"Turbidez (NTU)", None))
    # retranslateUi

