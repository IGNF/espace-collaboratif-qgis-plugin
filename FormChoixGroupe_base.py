# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormChoixGroupe_base.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogChoixGroupe(object):
    def setupUi(self, DialogChoixGroupe):
        DialogChoixGroupe.setObjectName("DialogChoixGroupe")
        DialogChoixGroupe.resize(269, 96)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogChoixGroupe)
        self.buttonBox.setGeometry(QtCore.QRect(10, 60, 251, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.lblGroupe = QtWidgets.QLabel(DialogChoixGroupe)
        self.lblGroupe.setGeometry(QtCore.QRect(10, 10, 261, 16))
        self.lblGroupe.setObjectName("lblGroupe")
        self.comboBoxGroupe = QtWidgets.QComboBox(DialogChoixGroupe)
        self.comboBoxGroupe.setGeometry(QtCore.QRect(10, 30, 251, 21))
        self.comboBoxGroupe.setObjectName("comboBoxGroupe")

        self.retranslateUi(DialogChoixGroupe)
        self.buttonBox.accepted.connect(DialogChoixGroupe.accept)
        self.buttonBox.rejected.connect(DialogChoixGroupe.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogChoixGroupe)

    def retranslateUi(self, DialogChoixGroupe):
        _translate = QtCore.QCoreApplication.translate
        DialogChoixGroupe.setWindowTitle(_translate("DialogChoixGroupe", "Choix du groupe"))
        self.lblGroupe.setText(_translate("DialogChoixGroupe", "Dans quel groupe souhaitez-vous travailler ? "))
