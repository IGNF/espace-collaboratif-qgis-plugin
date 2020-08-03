# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import QDialogButtonBox

from PyQt5 import QtCore, QtGui, QtWidgets, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormCompterGuichet_base.ui'))


class FormCompterGuichet(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, message, parent=None):
        super(FormCompterGuichet, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()
        self.labelCompteur.setText(message)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.ok)


    def ok(self):
        self.close()