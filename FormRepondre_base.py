# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormRepondre_base.ui'
#
# Created: Fri Oct 09 07:59:34 2015
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

class Ui_addResponse(object):
    def setupUi(self, addResponse):
        addResponse.setObjectName(_fromUtf8("addResponse"))
        addResponse.resize(360, 473)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("IGN"))
        addResponse.setWindowIcon(icon)
        self.btnCancel = QtGui.QDialogButtonBox(addResponse)
        self.btnCancel.setGeometry(QtCore.QRect(280, 440, 75, 23))
        self.btnCancel.setOrientation(QtCore.Qt.Horizontal)
        self.btnCancel.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.btnCancel.setCenterButtons(False)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.btnSend = QtGui.QPushButton(addResponse)
        self.btnSend.setGeometry(QtCore.QRect(130, 440, 141, 23))
        self.btnSend.setObjectName(_fromUtf8("btnSend"))
        self.lblStatut = QtGui.QLabel(addResponse)
        self.lblStatut.setGeometry(QtCore.QRect(10, 10, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.lblStatut.setFont(font)
        self.lblStatut.setObjectName(_fromUtf8("lblStatut"))
        self.cboxStatut = QtGui.QComboBox(addResponse)
        self.cboxStatut.setGeometry(QtCore.QRect(70, 10, 271, 22))
        self.cboxStatut.setObjectName(_fromUtf8("cboxStatut"))
        self.lblMessage = QtGui.QLabel(addResponse)
        self.lblMessage.setGeometry(QtCore.QRect(10, 50, 331, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.lblMessage.setFont(font)
        self.lblMessage.setObjectName(_fromUtf8("lblMessage"))
        self.textMessage = QtGui.QTextBrowser(addResponse)
        self.textMessage.setGeometry(QtCore.QRect(10, 70, 341, 91))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.textMessage.setFont(font)
        self.textMessage.setObjectName(_fromUtf8("textMessage"))
        self.lblOldResponse = QtGui.QLabel(addResponse)
        self.lblOldResponse.setGeometry(QtCore.QRect(10, 180, 331, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.lblOldResponse.setFont(font)
        self.lblOldResponse.setObjectName(_fromUtf8("lblOldResponse"))
        self.textOldRep = QtGui.QTextBrowser(addResponse)
        self.textOldRep.setGeometry(QtCore.QRect(10, 200, 341, 91))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.textOldRep.setFont(font)
        self.textOldRep.setObjectName(_fromUtf8("textOldRep"))
        self.lblNewResponse = QtGui.QLabel(addResponse)
        self.lblNewResponse.setGeometry(QtCore.QRect(10, 310, 331, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.lblNewResponse.setFont(font)
        self.lblNewResponse.setObjectName(_fromUtf8("lblNewResponse"))
        self.textNewRep = QtGui.QTextBrowser(addResponse)
        self.textNewRep.setGeometry(QtCore.QRect(10, 330, 341, 91))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.textNewRep.setFont(font)
        self.textNewRep.setReadOnly(False)
        self.textNewRep.setObjectName(_fromUtf8("textNewRep"))

        self.retranslateUi(addResponse)
        QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL(_fromUtf8("accepted()")), addResponse.accept)
        QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL(_fromUtf8("rejected()")), addResponse.reject)
        QtCore.QMetaObject.connectSlotsByName(addResponse)

    def retranslateUi(self, addResponse):
        addResponse.setWindowTitle(_translate("addResponse", "IGN RIPart : Ajout d\'une nouvelle réponse", None))
        self.btnSend.setText(_translate("addResponse", "Envoyer la réponse", None))
        self.lblStatut.setText(_translate("addResponse", "Statut", None))
        self.lblMessage.setText(_translate("addResponse", "Message de la remarque", None))
        self.lblOldResponse.setText(_translate("addResponse", "Réponse(s) antérieure(s)", None))
        self.lblNewResponse.setText(_translate("addResponse", "Nouvelle réponse", None))

