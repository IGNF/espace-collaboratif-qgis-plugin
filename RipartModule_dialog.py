# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RipartPluginDialog
                                 A QGIS plugin
 IGN_Ripart
                             -------------------
        begin                : 2015-01-21
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Alexia Chang-Wailing/IGN
        email                : a
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox


from PyQt4.QtCore import *


from core import Client
from core import Attribut
from core import ConstanteRipart

"""import sys 
sys.path.append(r'D:\eclipse\plugins\org.python.pydev_3.9.1.201501081637\pysrc') """


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'RipartModule_dialog_base.ui'))


class RipartPluginDialog(QtGui.QDialog, FORM_CLASS):
    
   
    
    def __init__(self, parent=None):
        """Constructor."""
        super(RipartPluginDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # Save reference to the QGIS interface
        
        self.btnConnect.clicked.connect(self.connect1)
        self.btnFoo.clicked.connect(self.foo)
        self.btnCancel.clicked.connect(self.close)
     
 
    
    @pyqtSlot()
    def connect1(self):
        login= self.lineEditLogin.text()
        
        pwd= self.lineEditPwd.text()
        QMessageBox.information(self,"Ripart",login)
        
        client = Client("demo", login,pwd)
        res= client.connect()
        QMessageBox.information(self,"Connection",res)
        
        
        
        
        
        
    @pyqtSlot()
    def foo(self):
        
        QMessageBox.information(self,"Ripart","FOO")
        
    @pyqtSlot()
    def cancel(self):
        self.reject
       