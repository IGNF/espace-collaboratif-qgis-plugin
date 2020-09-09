# -*- coding: utf-8 -*-
'''
Created on 30 sept. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
'''

import os


from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets

from qgis.PyQt import QtGui, uic, QtWidgets
from qgis.PyQt.QtWidgets import QMessageBox


from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, Qt

from qgis.PyQt.QtGui import QIcon

from . import FormInfo_base

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormInfo_base.ui'))

class FormInfo(QtWidgets.QDialog, FORM_CLASS):
    '''
    Fenêtre donnant des informations 
    '''
    
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
