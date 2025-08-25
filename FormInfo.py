# -*- coding: utf-8 -*-
"""
Created on 30 sept. 2015
Updated on 9 sept. 2020

version 4.0.6, 30/12/2021

@author: AChang-Wailing, EPeyrouse
"""

import os

from PyQt5 import QtCore
from qgis.PyQt import uic, QtWidgets, QtCore

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormInfo_base.ui'))


class FormInfo(QtWidgets.QDialog, FORM_CLASS):
    """
    Classe de dialogue qui affiche les informations sur le résultat des actions effectuées par l'utilisateur.
    Par exemple, les informations de connexion à l'espace collaboratif.
    """
    def __init__(self, parent=None) -> None:
        """
        Constructeur de la boite de dialogue d'informations intitulée "IGN Espace collaboratif"
        """
        super(FormInfo, self).__init__(parent)

        self.setupUi(self)

        # +20 en hauteur sinon le bouton OK est coupé
        self.setFixedSize(self.width(), self.height()+20)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.textInfo.setText("")
        self.textInfo.setGeometry(QtCore.QRect(150, 10, 341, 151))

        self.btnOK.clicked.connect(self.close)
        self.btnOK.setGeometry(QtCore.QRect(420, 165, 75, 23))
        self.btnOK.setText('OK')

        self.resize(511, 200)
        self.setWindowTitle("IGN Espace collaboratif")
        self.setStyleSheet("QDialog {background-color: rgb(255, 255, 255)}")

        self.logo.setOpenExternalLinks(True)
