# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SeeReportView_base.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QLabel,
    QPlainTextEdit, QSizePolicy, QWidget)

class Ui_SeeReportView(object):
    def setupUi(self, SeeReportView):
        if not SeeReportView.objectName():
            SeeReportView.setObjectName(u"SeeReportView")
        SeeReportView.resize(651, 580)
        font = QFont()
        font.setPointSize(1)
        SeeReportView.setFont(font)
        SeeReportView.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        self.lbl_generalInformation = QLabel(SeeReportView)
        self.lbl_generalInformation.setObjectName(u"lbl_generalInformation")
        self.lbl_generalInformation.setGeometry(QRect(10, 50, 191, 31))
        font1 = QFont()
        font1.setPointSize(9)
        font1.setBold(True)
        self.lbl_generalInformation.setFont(font1)
        self.lbl_contentNumberReport = QLabel(SeeReportView)
        self.lbl_contentNumberReport.setObjectName(u"lbl_contentNumberReport")
        self.lbl_contentNumberReport.setGeometry(QRect(110, 10, 331, 41))
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        self.lbl_contentNumberReport.setFont(font2)
        self.lbl_themes = QLabel(SeeReportView)
        self.lbl_themes.setObjectName(u"lbl_themes")
        self.lbl_themes.setGeometry(QRect(380, 50, 61, 31))
        self.lbl_themes.setFont(font1)
        self.lbl_description = QLabel(SeeReportView)
        self.lbl_description.setObjectName(u"lbl_description")
        self.lbl_description.setGeometry(QRect(10, 240, 101, 21))
        self.lbl_description.setFont(font1)
        self.lbl_documents = QLabel(SeeReportView)
        self.lbl_documents.setObjectName(u"lbl_documents")
        self.lbl_documents.setGeometry(QRect(10, 370, 161, 16))
        self.lbl_documents.setFont(font1)
        self.lbl_responses = QLabel(SeeReportView)
        self.lbl_responses.setObjectName(u"lbl_responses")
        self.lbl_responses.setGeometry(QRect(10, 450, 81, 21))
        self.lbl_responses.setFont(font1)
        self.lbl_displayGeneralInformation = QLabel(SeeReportView)
        self.lbl_displayGeneralInformation.setObjectName(u"lbl_displayGeneralInformation")
        self.lbl_displayGeneralInformation.setGeometry(QRect(10, 90, 351, 141))
        font3 = QFont()
        font3.setPointSize(8)
        self.lbl_displayGeneralInformation.setFont(font3)
        self.lbl_displayGeneralInformation.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.lbl_displayGeneralInformation.setWordWrap(True)
        self.lbl_displayDocuments = QLabel(SeeReportView)
        self.lbl_displayDocuments.setObjectName(u"lbl_displayDocuments")
        self.lbl_displayDocuments.setGeometry(QRect(10, 390, 631, 51))
        self.lbl_displayDocuments.setFont(font3)
        self.lbl_displayDocuments.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_displayDocuments.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.lbl_displayDocuments.setWordWrap(False)
        self.lbl_displayDocuments.setOpenExternalLinks(True)
        self.lbl_displayDocuments.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.lbl_displayDescription = QLabel(SeeReportView)
        self.lbl_displayDescription.setObjectName(u"lbl_displayDescription")
        self.lbl_displayDescription.setGeometry(QRect(10, 270, 631, 91))
        self.lbl_displayDescription.setFont(font3)
        self.lbl_displayDescription.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.lbl_displayDescription.setWordWrap(True)
        self.pte_displayThemes = QPlainTextEdit(SeeReportView)
        self.pte_displayThemes.setObjectName(u"pte_displayThemes")
        self.pte_displayThemes.setGeometry(QRect(370, 80, 271, 161))
        self.pte_displayThemes.setFont(font3)
        self.pte_displayThemes.setFrameShape(QFrame.Shape.NoFrame)
        self.pte_displayThemes.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.pte_displayThemes.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.pte_displayResponses = QPlainTextEdit(SeeReportView)
        self.pte_displayResponses.setObjectName(u"pte_displayResponses")
        self.pte_displayResponses.setGeometry(QRect(10, 480, 631, 91))
        self.pte_displayResponses.setFont(font3)
        self.pte_displayResponses.setFrameShape(QFrame.Shape.NoFrame)
        self.pte_displayResponses.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.pte_displayResponses.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.retranslateUi(SeeReportView)

        QMetaObject.connectSlotsByName(SeeReportView)
    # setupUi

    def retranslateUi(self, SeeReportView):
        SeeReportView.setWindowTitle(QCoreApplication.translate("SeeReportView", u"Voir un signalement", None))
        self.lbl_generalInformation.setText(QCoreApplication.translate("SeeReportView", u"Informations g\u00e9n\u00e9rales", None))
        self.lbl_contentNumberReport.setText("")
        self.lbl_themes.setText(QCoreApplication.translate("SeeReportView", u"Th\u00e8mes", None))
        self.lbl_description.setText(QCoreApplication.translate("SeeReportView", u"Description", None))
        self.lbl_documents.setText(QCoreApplication.translate("SeeReportView", u"Document(s) joint(s)", None))
        self.lbl_responses.setText(QCoreApplication.translate("SeeReportView", u"R\u00e9ponses", None))
        self.lbl_displayGeneralInformation.setText("")
        self.lbl_displayDocuments.setText("")
        self.lbl_displayDescription.setText("")
    # retranslateUi

