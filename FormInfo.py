# -*- coding: utf-8 -*-
'''
Created on 30 sept. 2015

@author: AChang-Wailing
'''
import os

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox

from PyQt4.QtCore import *
import FormInfo_base

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormInfo_base.ui'))

class FormInfo(QtGui.QDialog, FORM_CLASS):
    '''
    classdocs
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
        
        #self.setWindowFlags( Qt.WindowStaysOnTopHint)
        
        
    def addMessage(self, str):
        
        self.textInfo.append("sfqfs")