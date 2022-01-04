# -*- coding: utf-8 -*-
"""
Created on 4 janv. 2021
version 4.0.6, 30/12/2021
@author: EPeyrouse
"""

import os

from PyQt5 import QtCore
from qgis.PyQt import QtGui, uic, QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FeedbackInformationView_base.ui'))


class FeedbackInformationView(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue donnant des informations sur le résultat
    des actions effectuées par l'utilisateur
    """

    def __init__(self, parent=None):
        super(FeedbackInformationView, self).__init__(parent)
        self.setupUi(self)
