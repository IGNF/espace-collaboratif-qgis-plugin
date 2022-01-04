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
        DialogParametrage.resize(399, 237)
        DialogParametrage.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogParametrage)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QtCore.QRect(190, 200, 201, 31))
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
        self.radioButtonOui = QtWidgets.QRadioButton(DialogParametrage)
        self.radioButtonOui.setGeometry(QtCore.QRect(10, 140, 51, 20))
        self.radioButtonOui.setObjectName("radioButtonOui")
        self.radioButtonNon = QtWidgets.QRadioButton(DialogParametrage)
        self.radioButtonNon.setGeometry(QtCore.QRect(10, 170, 301, 20))
        self.radioButtonNon.setObjectName("radioButtonNon")
        self.lineEditCleGeoportailUser = QtWidgets.QLineEdit(DialogParametrage)
        self.lineEditCleGeoportailUser.setGeometry(QtCore.QRect(70, 140, 321, 22))
        self.lineEditCleGeoportailUser.setWhatsThis("")
        self.lineEditCleGeoportailUser.setAccessibleDescription("")
        self.lineEditCleGeoportailUser.setInputMask("")
        self.lineEditCleGeoportailUser.setText("")
        self.lineEditCleGeoportailUser.setPlaceholderText("")
        self.lineEditCleGeoportailUser.setObjectName("lineEditCleGeoportailUser")
        self.lblCleGeoportailUser = QtWidgets.QLabel(DialogParametrage)
        self.lblCleGeoportailUser.setGeometry(QtCore.QRect(10, 70, 391, 61))
        self.lblCleGeoportailUser.setTextFormat(QtCore.Qt.AutoText)
        self.lblCleGeoportailUser.setWordWrap(True)
        self.lblCleGeoportailUser.setObjectName("lblCleGeoportailUser")

        self.retranslateUi(DialogParametrage)
        QtCore.QMetaObject.connectSlotsByName(DialogParametrage)

    def retranslateUi(self, DialogParametrage):
        _translate = QtCore.QCoreApplication.translate
        DialogParametrage.setWindowTitle(_translate("DialogParametrage", "Choix du groupe"))
        self.lblGroupe.setText(_translate("DialogParametrage", "Dans quel groupe souhaitez-vous travailler ? "))
        self.radioButtonOui.setText(_translate("DialogParametrage", "Oui"))
        self.radioButtonNon.setText(_translate("DialogParametrage", "Non - Utiliser la clé Géoportail de démonstration"))
        self.lblCleGeoportailUser.setText(_translate("DialogParametrage", "<html><head/><body><p>Vous pouvez utiliser une clé Géoportail pour afficher les fonds IGN de votre groupe directement dans QGIS.</p><p>Disposez-vous de votre propre clé Géoportail ?</p></body></html>"))
