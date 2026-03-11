# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormChargerGuichet_base.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QAbstractScrollArea, QApplication,
    QDialog, QDialogButtonBox, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QWidget)

class Ui_DialogChargerGuichet(object):
    def setupUi(self, DialogChargerGuichet):
        if not DialogChargerGuichet.objectName():
            DialogChargerGuichet.setObjectName(u"DialogChargerGuichet")
        DialogChargerGuichet.resize(751, 707)
        DialogChargerGuichet.setStyleSheet(u"QDialog {background-color: rgb(255, 255, 255)}")
        self.buttonBox = QDialogButtonBox(DialogChargerGuichet)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(540, 670, 201, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)
        self.labelMonGuichet = QLabel(DialogChargerGuichet)
        self.labelMonGuichet.setObjectName(u"labelMonGuichet")
        self.labelMonGuichet.setGeometry(QRect(10, 40, 101, 21))
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.labelMonGuichet.setFont(font)
        self.labelFondsGeoservices = QLabel(DialogChargerGuichet)
        self.labelFondsGeoservices.setObjectName(u"labelFondsGeoservices")
        self.labelFondsGeoservices.setGeometry(QRect(10, 370, 151, 21))
        self.labelFondsGeoservices.setFont(font)
        self.tableWidgetMonGuichet = QTableWidget(DialogChargerGuichet)
        if (self.tableWidgetMonGuichet.columnCount() < 3):
            self.tableWidgetMonGuichet.setColumnCount(3)
        self.tableWidgetMonGuichet.setObjectName(u"tableWidgetMonGuichet")
        self.tableWidgetMonGuichet.setEnabled(True)
        self.tableWidgetMonGuichet.setGeometry(QRect(10, 70, 731, 261))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidgetMonGuichet.sizePolicy().hasHeightForWidth())
        self.tableWidgetMonGuichet.setSizePolicy(sizePolicy)
        self.tableWidgetMonGuichet.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableWidgetMonGuichet.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.tableWidgetMonGuichet.setAutoScroll(True)
        self.tableWidgetMonGuichet.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.tableWidgetMonGuichet.setShowGrid(False)
        self.tableWidgetMonGuichet.setGridStyle(Qt.PenStyle.NoPen)
        self.tableWidgetMonGuichet.setRowCount(0)
        self.tableWidgetMonGuichet.setColumnCount(3)
        self.tableWidgetMonGuichet.horizontalHeader().setVisible(True)
        self.tableWidgetMonGuichet.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidgetMonGuichet.horizontalHeader().setMinimumSectionSize(30)
        self.tableWidgetMonGuichet.horizontalHeader().setDefaultSectionSize(225)
        self.tableWidgetMonGuichet.horizontalHeader().setHighlightSections(False)
        self.tableWidgetMonGuichet.horizontalHeader().setStretchLastSection(False)
        self.tableWidgetMonGuichet.verticalHeader().setVisible(False)
        self.tableWidgetMonGuichet.verticalHeader().setCascadingSectionResizes(True)
        self.tableWidgetMonGuichet.verticalHeader().setMinimumSectionSize(37)
        self.tableWidgetMonGuichet.verticalHeader().setDefaultSectionSize(37)
        self.tableWidgetMonGuichet.verticalHeader().setHighlightSections(False)
        self.tableWidgetMonGuichet.verticalHeader().setStretchLastSection(False)
        self.tableWidgetFondsGeoservices = QTableWidget(DialogChargerGuichet)
        if (self.tableWidgetFondsGeoservices.columnCount() < 3):
            self.tableWidgetFondsGeoservices.setColumnCount(3)
        self.tableWidgetFondsGeoservices.setObjectName(u"tableWidgetFondsGeoservices")
        self.tableWidgetFondsGeoservices.setGeometry(QRect(10, 400, 731, 261))
        self.tableWidgetFondsGeoservices.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableWidgetFondsGeoservices.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.tableWidgetFondsGeoservices.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.tableWidgetFondsGeoservices.setShowGrid(False)
        self.tableWidgetFondsGeoservices.setGridStyle(Qt.PenStyle.NoPen)
        self.tableWidgetFondsGeoservices.setColumnCount(3)
        self.tableWidgetFondsGeoservices.horizontalHeader().setVisible(True)
        self.tableWidgetFondsGeoservices.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidgetFondsGeoservices.horizontalHeader().setMinimumSectionSize(30)
        self.tableWidgetFondsGeoservices.horizontalHeader().setDefaultSectionSize(225)
        self.tableWidgetFondsGeoservices.horizontalHeader().setHighlightSections(False)
        self.tableWidgetFondsGeoservices.horizontalHeader().setStretchLastSection(False)
        self.tableWidgetFondsGeoservices.verticalHeader().setVisible(False)
        self.tableWidgetFondsGeoservices.verticalHeader().setCascadingSectionResizes(True)
        self.tableWidgetFondsGeoservices.verticalHeader().setHighlightSections(False)
        self.tableWidgetFondsGeoservices.verticalHeader().setStretchLastSection(False)
        self.labelGroupeActif = QLabel(DialogChargerGuichet)
        self.labelGroupeActif.setObjectName(u"labelGroupeActif")
        self.labelGroupeActif.setGeometry(QRect(10, 10, 621, 21))
        font1 = QFont()
        font1.setPointSize(9)
        font1.setBold(True)
        font1.setItalic(False)
        self.labelGroupeActif.setFont(font1)
        self.pushButton_checkAllBoxes_MonGuichet = QPushButton(DialogChargerGuichet)
        self.pushButton_checkAllBoxes_MonGuichet.setObjectName(u"pushButton_checkAllBoxes_MonGuichet")
        self.pushButton_checkAllBoxes_MonGuichet.setGeometry(QRect(650, 30, 93, 28))
        self.pushButton_checkAllBoxes_FondsGeoservices = QPushButton(DialogChargerGuichet)
        self.pushButton_checkAllBoxes_FondsGeoservices.setObjectName(u"pushButton_checkAllBoxes_FondsGeoservices")
        self.pushButton_checkAllBoxes_FondsGeoservices.setGeometry(QRect(650, 360, 93, 28))

        self.retranslateUi(DialogChargerGuichet)

        QMetaObject.connectSlotsByName(DialogChargerGuichet)
    # setupUi

    def retranslateUi(self, DialogChargerGuichet):
        DialogChargerGuichet.setWindowTitle(QCoreApplication.translate("DialogChargerGuichet", u"Charger les couches de mon groupe", None))
        self.labelMonGuichet.setText(QCoreApplication.translate("DialogChargerGuichet", u"Mon guichet", None))
        self.labelFondsGeoservices.setText(QCoreApplication.translate("DialogChargerGuichet", u"Fonds G\u00e9oservices", None))
        self.labelGroupeActif.setText("")
        self.pushButton_checkAllBoxes_MonGuichet.setText(QCoreApplication.translate("DialogChargerGuichet", u"Tout charger", None))
        self.pushButton_checkAllBoxes_FondsGeoservices.setText(QCoreApplication.translate("DialogChargerGuichet", u"Tout charger", None))
    # retranslateUi

