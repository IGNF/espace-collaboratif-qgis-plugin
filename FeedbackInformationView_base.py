# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FeedbackInformationView_base.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FeedbackInformationView(object):
    def setupUi(self, FeedbackInformationView):
        FeedbackInformationView.setObjectName("FeedbackInformationView")
        FeedbackInformationView.resize(499, 230)
        FeedbackInformationView.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.buttonBox = QtWidgets.QDialogButtonBox(FeedbackInformationView)
        self.buttonBox.setGeometry(QtCore.QRect(390, 190, 101, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.MessageTextBrowser = QtWidgets.QTextBrowser(FeedbackInformationView)
        self.MessageTextBrowser.setGeometry(QtCore.QRect(150, 10, 341, 171))
        self.MessageTextBrowser.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.MessageTextBrowser.setObjectName("MessageTextBrowser")
        self.logoGroup = QtWidgets.QLabel(FeedbackInformationView)
        self.logoGroup.setGeometry(QtCore.QRect(10, 10, 121, 141))
        self.logoGroup.setText("")
        self.logoGroup.setPixmap(QtGui.QPixmap("images/logo_IGN.png"))
        self.logoGroup.setScaledContents(True)
        self.logoGroup.setOpenExternalLinks(True)
        self.logoGroup.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.logoGroup.setObjectName("logoGroup")

        self.retranslateUi(FeedbackInformationView)
        self.buttonBox.accepted.connect(FeedbackInformationView.accept)
        QtCore.QMetaObject.connectSlotsByName(FeedbackInformationView)

    def retranslateUi(self, FeedbackInformationView):
        _translate = QtCore.QCoreApplication.translate
        FeedbackInformationView.setWindowTitle(_translate("FeedbackInformationView", "IGN Espace collaboratif"))
