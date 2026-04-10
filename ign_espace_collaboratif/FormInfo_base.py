# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormInfo_base.ui'
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
    QApplication, QDialog, QFrame, QLabel,
    QPushButton, QSizePolicy, QTextBrowser, QWidget,
)
class Ui_InfoDialog(object):
    def setupUi(self, InfoDialog):
        if not InfoDialog.objectName():
            InfoDialog.setObjectName(u"InfoDialog")
        InfoDialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        InfoDialog.resize(511, 176)
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        InfoDialog.setPalette(palette)
        InfoDialog.setAutoFillBackground(False)
        InfoDialog.setSizeGripEnabled(True)
        InfoDialog.setModal(True)
        self.label = QLabel(InfoDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 46, 13))
        self.label.setPixmap(QPixmap(u":/plugins/RipartPlugin/icon.png"))
        self.logo = QLabel(InfoDialog)
        self.logo.setObjectName(u"logo")
        self.logo.setGeometry(QRect(10, 0, 121, 141))
        font = QFont()
        font.setPointSize(10)
        self.logo.setFont(font)
        self.logo.setPixmap(QPixmap(u":/plugins/RipartPlugin/images/logo_IGN.png"))
        self.logo.setScaledContents(True)
        self.textInfo = QTextBrowser(InfoDialog)
        self.textInfo.setObjectName(u"textInfo")
        self.textInfo.setGeometry(QRect(150, 10, 341, 121))
        palette1 = QPalette()
        brush1 = QBrush(QColor(0, 0, 0, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush1)
        brush2 = QBrush(QColor(81, 81, 81, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        brush3 = QBrush(QColor(120, 120, 120, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush3)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush3)
        self.textInfo.setPalette(palette1)
        font1 = QFont()
        font1.setPointSize(9)
        self.textInfo.setFont(font1)
        self.textInfo.setFrameShape(QFrame.Shape.NoFrame)
        self.textInfo.setLineWidth(0)
        self.btnOK = QPushButton(InfoDialog)
        self.btnOK.setObjectName(u"btnOK")
        self.btnOK.setGeometry(QRect(430, 140, 75, 23))

        self.retranslateUi(InfoDialog)

        QMetaObject.connectSlotsByName(InfoDialog)
    # setupUi

    def retranslateUi(self, InfoDialog):
        InfoDialog.setWindowTitle(QCoreApplication.translate("InfoDialog", u"Espace Collaboratif IGN", None))
        self.label.setText("")
        self.logo.setText("")
        self.btnOK.setText(QCoreApplication.translate("InfoDialog", u"Ok", None))
    # retranslateUi

