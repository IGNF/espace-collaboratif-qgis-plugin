# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ReplyReportView_base.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QLabel,
    QPlainTextEdit, QPushButton, QSizePolicy, QWidget)

class Ui_ReplyReportView(object):
    def setupUi(self, ReplyReportView):
        if not ReplyReportView.objectName():
            ReplyReportView.setObjectName(u"ReplyReportView")
        ReplyReportView.resize(401, 328)
        ReplyReportView.setStyleSheet(u"QDialog {background-color: rgb(255, 255, 255)}")
        self.StatutItemsSourceComboBox = QComboBox(ReplyReportView)
        self.StatutItemsSourceComboBox.setObjectName(u"StatutItemsSourceComboBox")
        self.StatutItemsSourceComboBox.setGeometry(QRect(120, 250, 271, 31))
        self.btn_sendResponse = QPushButton(ReplyReportView)
        self.btn_sendResponse.setObjectName(u"btn_sendResponse")
        self.btn_sendResponse.setGeometry(QRect(180, 290, 91, 31))
        self.lbl_newStatut = QLabel(ReplyReportView)
        self.lbl_newStatut.setObjectName(u"lbl_newStatut")
        self.lbl_newStatut.setGeometry(QRect(10, 240, 111, 41))
        font = QFont()
        font.setPointSize(9)
        self.lbl_newStatut.setFont(font)
        self.lbl_response = QLabel(ReplyReportView)
        self.lbl_response.setObjectName(u"lbl_response")
        self.lbl_response.setGeometry(QRect(10, 55, 91, 31))
        self.lbl_response.setFont(font)
        self.lbl_numberReportLabel = QLabel(ReplyReportView)
        self.lbl_numberReportLabel.setObjectName(u"lbl_numberReportLabel")
        self.lbl_numberReportLabel.setGeometry(QRect(10, 15, 381, 31))
        font1 = QFont()
        font1.setPointSize(9)
        font1.setBold(True)
        self.lbl_numberReportLabel.setFont(font1)
        self.lbl_numberReportLabel.setWordWrap(True)
        self.lbl_numberReportLabel.setIndent(-1)
        self.pte_NewResponse = QPlainTextEdit(ReplyReportView)
        self.pte_NewResponse.setObjectName(u"pte_NewResponse")
        self.pte_NewResponse.setGeometry(QRect(20, 100, 361, 141))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pte_NewResponse.sizePolicy().hasHeightForWidth())
        self.pte_NewResponse.setSizePolicy(sizePolicy)

        self.retranslateUi(ReplyReportView)

        QMetaObject.connectSlotsByName(ReplyReportView)
    # setupUi

    def retranslateUi(self, ReplyReportView):
        ReplyReportView.setWindowTitle(QCoreApplication.translate("ReplyReportView", u"R\u00e9pondre au(x) signalement(s)", None))
        self.btn_sendResponse.setText(QCoreApplication.translate("ReplyReportView", u"Enregistrer", None))
#if QT_CONFIG(tooltip)
        self.lbl_newStatut.setToolTip(QCoreApplication.translate("ReplyReportView", u"<html><head/><body><p>A propos des statuts de r\u00e9ponse</p><p><br/></p><p>En cours de traitement : le signalement est en cours d'analyse ou de traitement par un responsable.</p><p><br/></p><p>En attente de saisie : la prise en compte effective du signalement n\u00e9cessite un laps de temps plus long (attente de passage terrain par exemple). La mise \u00e0 jour des donn\u00e9es est donc diff\u00e9r\u00e9e.</p><p><br/></p><p>Pris en compte : le signalement est clos et a \u00e9t\u00e9 pris en compte dans nos donn\u00e9es.</p><p><br/></p><p>D\u00e9j\u00e0 pris en compte : le signalement est clos. Aucune modification n'a \u00e9t\u00e9 faite dans les donn\u00e9es car la mise \u00e0 jour avait d\u00e9j\u00e0 \u00e9t\u00e9 faite par ailleurs.</p><p><br/></p><p>Rejet\u00e9 (hors sp\u00e9c.) : le signalement est clos et n'a pas \u00e9t\u00e9 pris en compte car il n'entre pas dans le champs des sp\u00e9cifications des donn\u00e9es.</p><p><br/></p><p>Rejet\u00e9 (hors de propos) : le signalement est clos et n'a pas \u00e9"
                        "t\u00e9 pris en compte car hors de propos par rapport aux donn\u00e9es.</p><p><br/></p><p><br/></p><p>La cl\u00f4ture d'un signalement (un des 4 derniers statuts) n\u00e9cessite l'intervention d'un valideur : votre gestionnaire de groupe. Le statut du signalement restera \u00e0 en attente de validation tant qu'il n'aura pas valid\u00e9 votre r\u00e9ponse.</p><p><br/></p><p>Si le gestionnaire de groupe l'a autoris\u00e9, la cl\u00f4ture du signalement peut \u00e9galement \u00eatre automatique d\u00e8s lors que vous choisissez un des 4 derniers statuts. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_newStatut.setText(QCoreApplication.translate("ReplyReportView", u"Nouveau statut", None))
        self.lbl_response.setText(QCoreApplication.translate("ReplyReportView", u"Ma r\u00e9ponse", None))
        self.lbl_numberReportLabel.setText("")
    # retranslateUi

