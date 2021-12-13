# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SeeReportView_base.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SeeReportView(object):
    def setupUi(self, SeeReportView):
        SeeReportView.setObjectName("SeeReportView")
        SeeReportView.resize(587, 580)
        font = QtGui.QFont()
        font.setPointSize(4)
        SeeReportView.setFont(font)
        self.lbl_generalInformation = QtWidgets.QLabel(SeeReportView)
        self.lbl_generalInformation.setGeometry(QtCore.QRect(10, 60, 191, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_generalInformation.setFont(font)
        self.lbl_generalInformation.setObjectName("lbl_generalInformation")
        self.lbl_contentNumberReport = QtWidgets.QLabel(SeeReportView)
        self.lbl_contentNumberReport.setGeometry(QtCore.QRect(110, 10, 331, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_contentNumberReport.setFont(font)
        self.lbl_contentNumberReport.setText("")
        self.lbl_contentNumberReport.setObjectName("lbl_contentNumberReport")
        self.lbl_themes = QtWidgets.QLabel(SeeReportView)
        self.lbl_themes.setGeometry(QtCore.QRect(400, 60, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_themes.setFont(font)
        self.lbl_themes.setObjectName("lbl_themes")
        self.lbl_groupDescription = QtWidgets.QLabel(SeeReportView)
        self.lbl_groupDescription.setGeometry(QtCore.QRect(10, 240, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_groupDescription.setFont(font)
        self.lbl_groupDescription.setObjectName("lbl_groupDescription")
        self.lbl_documents = QtWidgets.QLabel(SeeReportView)
        self.lbl_documents.setGeometry(QtCore.QRect(10, 370, 161, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_documents.setFont(font)
        self.lbl_documents.setObjectName("lbl_documents")
        self.lbl_responses = QtWidgets.QLabel(SeeReportView)
        self.lbl_responses.setGeometry(QtCore.QRect(10, 480, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_responses.setFont(font)
        self.lbl_responses.setObjectName("lbl_responses")
        self.lbl_displayGeneralInformation = QtWidgets.QLabel(SeeReportView)
        self.lbl_displayGeneralInformation.setGeometry(QtCore.QRect(10, 90, 331, 141))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lbl_displayGeneralInformation.setFont(font)
        self.lbl_displayGeneralInformation.setText("")
        self.lbl_displayGeneralInformation.setObjectName("lbl_displayGeneralInformation")

        self.retranslateUi(SeeReportView)
        QtCore.QMetaObject.connectSlotsByName(SeeReportView)

    def retranslateUi(self, SeeReportView):
        _translate = QtCore.QCoreApplication.translate
        SeeReportView.setWindowTitle(_translate("SeeReportView", "Voir un signalement"))
        self.lbl_generalInformation.setText(_translate("SeeReportView", "Informations générales"))
        self.lbl_themes.setText(_translate("SeeReportView", "Thèmes"))
        self.lbl_groupDescription.setText(_translate("SeeReportView", "Description"))
        self.lbl_documents.setText(_translate("SeeReportView", "Document(s) joint(s)"))
        self.lbl_responses.setText(_translate("SeeReportView", "Réponses"))
