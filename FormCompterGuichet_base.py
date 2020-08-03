# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormCompterGuichet_base.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DialogCompteur(object):
    def setupUi(self, DialogCompteur):
        DialogCompteur.setObjectName("DialogCompteur")
        DialogCompteur.resize(252, 459)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogCompteur)
        self.buttonBox.setGeometry(QtCore.QRect(70, 420, 101, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.labelCompteur = QtWidgets.QLabel(DialogCompteur)
        self.labelCompteur.setGeometry(QtCore.QRect(10, 10, 231, 401))
        self.labelCompteur.setText("")
        self.labelCompteur.setObjectName("labelCompteur")

        self.retranslateUi(DialogCompteur)
        QtCore.QMetaObject.connectSlotsByName(DialogCompteur)

    def retranslateUi(self, DialogCompteur):
        _translate = QtCore.QCoreApplication.translate
        DialogCompteur.setWindowTitle(_translate("DialogCompteur", "Compteur"))
