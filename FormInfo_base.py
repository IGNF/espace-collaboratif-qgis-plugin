# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FormInfo_base.ui'
#
# Created: Mon Nov 09 08:37:36 2015
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

class Ui_InfoDialog(object):
    def setupUi(self, InfoDialog):
        InfoDialog.setObjectName(_fromUtf8("InfoDialog"))
        InfoDialog.setWindowModality(QtCore.Qt.WindowModal)
        InfoDialog.resize(511, 176)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        InfoDialog.setPalette(palette)
        InfoDialog.setAutoFillBackground(False)
        InfoDialog.setSizeGripEnabled(True)
        InfoDialog.setModal(True)
        self.label = QtGui.QLabel(InfoDialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 46, 13))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/RipartPlugin/icon.png")))
        self.label.setObjectName(_fromUtf8("label"))
        self.logo = QtGui.QLabel(InfoDialog)
        self.logo.setGeometry(QtCore.QRect(10, 0, 121, 141))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.logo.setFont(font)
        self.logo.setText(_fromUtf8(""))
        self.logo.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/RipartPlugin/images/logo_IGN.png")))
        self.logo.setScaledContents(True)
        self.logo.setObjectName(_fromUtf8("logo"))
        self.textInfo = QtGui.QTextBrowser(InfoDialog)
        self.textInfo.setGeometry(QtCore.QRect(150, 10, 341, 121))
        self.textInfo.setFrameShape(QtGui.QFrame.NoFrame)
        self.textInfo.setLineWidth(0)
        self.textInfo.setObjectName(_fromUtf8("textInfo"))
        self.btnOK = QtGui.QPushButton(InfoDialog)
        self.btnOK.setGeometry(QtCore.QRect(430, 140, 75, 23))
        self.btnOK.setObjectName(_fromUtf8("btnOK"))

        self.retranslateUi(InfoDialog)
        QtCore.QMetaObject.connectSlotsByName(InfoDialog)

    def retranslateUi(self, InfoDialog):
        InfoDialog.setWindowTitle(_translate("InfoDialog", "IGN RIPart", None))
        self.btnOK.setText(_translate("InfoDialog", "Ok", None))

