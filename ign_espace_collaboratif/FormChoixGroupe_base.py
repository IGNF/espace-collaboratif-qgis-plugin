# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormChoixGroupe_base.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from .qt_compat import (
    QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt,
    QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform,
    QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QLabel, QSizePolicy,
    QToolButton, QWidget,
)

class Ui_DialogParametrage(object):
    def setupUi(self, DialogParametrage):
        if not DialogParametrage.objectName():
            DialogParametrage.setObjectName(u"DialogParametrage")
        DialogParametrage.resize(345, 324)
        DialogParametrage.setStyleSheet(u"QDialog {background-color: rgb(255, 255, 255)}")
        self.lblGroupComment = QLabel(DialogParametrage)
        self.lblGroupComment.setObjectName(u"lblGroupComment")
        self.lblGroupComment.setGeometry(QRect(10, 20, 331, 51))
        font = QFont()
        font.setItalic(True)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.lblGroupComment.setFont(font)
        self.lblGroupComment.setAutoFillBackground(False)
        self.lblGroupComment.setWordWrap(True)
        self.comboBoxGroup = QComboBox(DialogParametrage)
        self.comboBoxGroup.setObjectName(u"comboBoxGroup")
        self.comboBoxGroup.setGeometry(QRect(10, 70, 321, 22))
        self.lblGroup = QLabel(DialogParametrage)
        self.lblGroup.setObjectName(u"lblGroup")
        self.lblGroup.setGeometry(QRect(10, 0, 61, 21))
        font1 = QFont()
        font1.setPointSize(9)
        font1.setBold(True)
        self.lblGroup.setFont(font1)
        self.lblWorkZone = QLabel(DialogParametrage)
        self.lblWorkZone.setObjectName(u"lblWorkZone")
        self.lblWorkZone.setGeometry(QRect(10, 140, 121, 16))
        self.lblWorkZone.setFont(font1)
        self.lblWorkZoneComment = QLabel(DialogParametrage)
        self.lblWorkZoneComment.setObjectName(u"lblWorkZoneComment")
        self.lblWorkZoneComment.setGeometry(QRect(10, 160, 291, 41))
        font2 = QFont()
        font2.setItalic(True)
        self.lblWorkZoneComment.setFont(font2)
        self.lblWorkZoneComment.setWordWrap(True)
        self.comboBoxWorkZone = QComboBox(DialogParametrage)
        self.comboBoxWorkZone.setObjectName(u"comboBoxWorkZone")
        self.comboBoxWorkZone.setGeometry(QRect(10, 210, 281, 22))
        self.toolButtonShapeFile = QToolButton(DialogParametrage)
        self.toolButtonShapeFile.setObjectName(u"toolButtonShapeFile")
        self.toolButtonShapeFile.setGeometry(QRect(300, 210, 27, 22))
        self.label = QLabel(DialogParametrage)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 100, 261, 16))
        self.checkBox = QCheckBox(DialogParametrage)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(280, 100, 78, 20))
        self.buttonBox = QDialogButtonBox(DialogParametrage)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QRect(70, 270, 201, 31))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)
        self.buttonBox.setCenterButtons(True)

        self.retranslateUi(DialogParametrage)

        QMetaObject.connectSlotsByName(DialogParametrage)
    # setupUi

    def retranslateUi(self, DialogParametrage):
        DialogParametrage.setWindowTitle(QCoreApplication.translate("DialogParametrage", u"Param\u00e8tres de travail", None))
        self.lblGroupComment.setText(QCoreApplication.translate("DialogParametrage", u"Choississez parmi les groupes auxquels vous appartenez celui dans lequel vous souhaitez travailler", None))
        self.lblGroup.setText(QCoreApplication.translate("DialogParametrage", u"Groupe", None))
        self.lblWorkZone.setText(QCoreApplication.translate("DialogParametrage", u"Zone de travail", None))
        self.lblWorkZoneComment.setText(QCoreApplication.translate("DialogParametrage", u"La zone de travail sera utilis\u00e9e pour t\u00e9l\u00e9charger les signalements ou les donn\u00e9es de votre groupe", None))
        self.toolButtonShapeFile.setText(QCoreApplication.translate("DialogParametrage", u"...", None))
        self.label.setText(QCoreApplication.translate("DialogParametrage", u"T\u00e9l\u00e9chargement des signalements publics", None))
        self.checkBox.setText("")
    # retranslateUi

