# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormConnexion_dialog_base.ui'
#
# Created: Wed Sep 30 15:16:27 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_RipartPlugin(object):
    def setupUi(self, RipartPlugin):
        RipartPlugin.setObjectName(_fromUtf8("RipartPlugin"))
        RipartPlugin.resize(401, 145)
        RipartPlugin.setAutoFillBackground(False)
        RipartPlugin.setSizeGripEnabled(True)
        RipartPlugin.setModal(True)
        self.btnConnect = QtGui.QPushButton(RipartPlugin)
        self.btnConnect.setGeometry(QtCore.QRect(230, 70, 75, 23))
        self.btnConnect.setObjectName(_fromUtf8("btnConnect"))
        self.lblLogin = QtGui.QLabel(RipartPlugin)
        self.lblLogin.setGeometry(QtCore.QRect(111, 11, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblLogin.setFont(font)
        self.lblLogin.setObjectName(_fromUtf8("lblLogin"))
        self.lblPwd = QtGui.QLabel(RipartPlugin)
        self.lblPwd.setGeometry(QtCore.QRect(111, 40, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lblPwd.setFont(font)
        self.lblPwd.setObjectName(_fromUtf8("lblPwd"))
        self.lineEditLogin = QtGui.QLineEdit(RipartPlugin)
        self.lineEditLogin.setGeometry(QtCore.QRect(230, 11, 161, 20))
        self.lineEditLogin.setObjectName(_fromUtf8("lineEditLogin"))
        self.lineEditPwd = QtGui.QLineEdit(RipartPlugin)
        self.lineEditPwd.setGeometry(QtCore.QRect(230, 40, 161, 20))
        self.lineEditPwd.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditPwd.setObjectName(_fromUtf8("lineEditPwd"))
        self.btnCancel = QtGui.QPushButton(RipartPlugin)
        self.btnCancel.setGeometry(QtCore.QRect(310, 70, 75, 23))
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.label = QtGui.QLabel(RipartPlugin)
        self.label.setGeometry(QtCore.QRect(20, 20, 46, 13))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/RipartPlugin/icon.png")))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(RipartPlugin)
        self.label_2.setGeometry(QtCore.QRect(10, 0, 91, 91))
        self.label_2.setText(_fromUtf8(""))
        self.label_2.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/RipartPlugin/images/logo_IGN.png")))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lblErreur = QtGui.QLabel(RipartPlugin)
        self.lblErreur.setGeometry(QtCore.QRect(10, 100, 381, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.lblErreur.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Sans Serif"))
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.lblErreur.setFont(font)
        self.lblErreur.setObjectName(_fromUtf8("lblErreur"))

        self.retranslateUi(RipartPlugin)
        QtCore.QObject.connect(RipartPlugin, QtCore.SIGNAL(_fromUtf8("accepted()")), self.btnConnect.click)
        QtCore.QMetaObject.connectSlotsByName(RipartPlugin)

    def retranslateUi(self, RipartPlugin):
        RipartPlugin.setWindowTitle(_translate("RipartPlugin", "Connexion au service Ripart", None))
        self.btnConnect.setWhatsThis(_translate("RipartPlugin", "<html><head/><body><p>connexion au service</p></body></html>", None))
        self.btnConnect.setText(_translate("RipartPlugin", "Connecter", None))
        self.lblLogin.setText(_translate("RipartPlugin", "Votre login", None))
        self.lblPwd.setText(_translate("RipartPlugin", "Votre mot de passe", None))
        self.btnCancel.setText(_translate("RipartPlugin", "Annuler", None))
        self.lblErreur.setText(_translate("RipartPlugin", "Message d\'erreur", None))


