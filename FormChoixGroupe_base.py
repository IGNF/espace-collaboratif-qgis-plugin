# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormChoixGroupe_base.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogParametrage(object):
    def setupUi(self, DialogParametrage):
        DialogParametrage.setObjectName("DialogParametrage")
        DialogParametrage.resize(272, 102)
        DialogParametrage.setStyleSheet("QDialog {background-color: rgb(255, 255, 255)}")
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogParametrage)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QtCore.QRect(40, 60, 201, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.lblGroupe = QtWidgets.QLabel(DialogParametrage)
        self.lblGroupe.setGeometry(QtCore.QRect(10, 10, 261, 16))
        self.lblGroupe.setObjectName("lblGroupe")
        self.comboBoxGroupe = QtWidgets.QComboBox(DialogParametrage)
        self.comboBoxGroupe.setGeometry(QtCore.QRect(10, 30, 251, 21))
        self.comboBoxGroupe.setObjectName("comboBoxGroupe")

        self.retranslateUi(DialogParametrage)
        QtCore.QMetaObject.connectSlotsByName(DialogParametrage)

    def retranslateUi(self, DialogParametrage):
        _translate = QtCore.QCoreApplication.translate
        DialogParametrage.setWindowTitle(_translate("DialogParametrage", "Choix du groupe"))
        self.lblGroupe.setText(_translate("DialogParametrage", "Dans quel groupe souhaitez-vous travailler ? "))
