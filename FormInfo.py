# -*- coding: utf-8 -*-
'''
Created on 30 sept. 2015
Updated on 9 sept. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse
'''

import os

from PyQt5 import QtCore
from qgis.PyQt import QtGui, uic, QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormInfo_base.ui'))


class FormInfo(QtWidgets.QDialog, FORM_CLASS):
    """
    Fenêtre donnant des informations
    """
    
    def __init__(self, parent=None):
        """Constructor."""
         
        super(FormInfo, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # Save reference to the QGIS interface
        
        self.textInfo.setText("")
        self.btnOK.clicked.connect(self.close)

        self.resize(511, 200)
        self.setWindowTitle("IGN Espace collaboratif")
        self.textInfo.setGeometry(QtCore.QRect(150, 10, 341, 151))
        self.btnOK.setGeometry(QtCore.QRect(420, 170, 75, 23))
        self.logo = QtWidgets.QLabel(self)
        self.logo.setGeometry(QtCore.QRect(10, 0, 121, 141))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.logo.setFont(font)
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap(":/plugins/RipartPlugin/images/no_logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        #self.logo.setPixmap(QtGui.QPixmap(":/plugins/RipartPlugin/images/no_logo.png"))
        #self.logo.setScaledContents(True)
