# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RipartPlugin
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
import logging
from core.RipartLoggerCl import RipartLogger

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL, Qt
from PyQt4.QtGui import QAction, QIcon, QMenu
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox,QToolButton
from qgis.core import *



# Initialize Qt resources from file resources.py
import resources

# Import the code for the dialog
from FormConnexion_dialog import FormConnexionDialog
from FormInfo import FormInfo

from Contexte import Contexte
from core.Client import Client

import os.path
from qgis._core import QgsProject,  QgsMessageLog

from ImporterRipart import ImporterRipart
from RipartException import RipartException

from FormRepondre import FormRepondreDialog
from RepondreRipart import RepondreRipart

class RipartPlugin:
    """QGIS Plugin Implementation."""
    
    context=None
    logger= None

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.logger=RipartLogger("RipartPlugin").getRipartLogger()
        
        
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RipartPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        
        #Init Contexte
        #self.context= Contexte.getInstance(self,QgsProject.instance())

        # Create the dialog (after translation) and keep reference
        self.dlgConnexion = FormConnexionDialog()
        
        self.dlgInfo=FormInfo()
        
     

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&IGN_Ripart')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RipartPlugin')
        self.toolbar.setObjectName(u'RipartPlugin')
        
        
        #self.contexte.setProjectParams(QgsProject)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RipartPlugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)


        return action



    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/RipartPlugin/images/connect.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Connexion au service RIPart'),
            callback=self.run,
            status_tip=self.tr(u'Connexion au service RIPart'),
            parent=self.iface.mainWindow())
      
        
        icon_path = ':/plugins/RipartPlugin/images/update.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Télécharger les remarques RIPart'),
            callback=self.downloadRemarks,
            status_tip=self.tr(u'Télécharger les remarques RIPart'),
            parent=self.iface.mainWindow())
        
        
        icon_path = ':/plugins/RipartPlugin/images/answer.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Répondre à une remarque RIPart'),
            callback=self.answerToRemark,
            status_tip=self.tr(u'Répondre à une remarque RIPart'),
            parent=self.iface.mainWindow())
        
        icon_path = ':/plugins/RipartPlugin/images/create.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Nouvelle remarque'),
            callback=self.createRemark,
            status_tip=self.tr(u'Nouvelle remarque'),
            parent=self.iface.mainWindow())
        
        icon_path = ':/plugins/RipartPlugin/images/cleaning.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Supprimer les remarques de la carte en cours'),
            callback=self.removeRemarks,
            status_tip=self.tr(u'Supprimer les remarques de la carte en cours'),
            parent=self.iface.mainWindow())
        
     
           
        self.config = QAction(QIcon(":/plugins/RipartPlugin/images/config.png"), u"Configurer l'add-in RIPart", self.iface.mainWindow())
        self.help = QAction(QIcon(":/plugins/RipartPlugin/images/Book.png"), "Ouvrir le manuel utilisateur de l'add-in RIPart", self.iface.mainWindow())
        self.log= QAction(QIcon(":/plugins/RipartPlugin/images/Log.png"), "Ouvrir le fichier de log de l'add-in RIPart", self.iface.mainWindow())
        self.about = QAction(QIcon(":/plugins/RipartPlugin/images/About.png"), "A propos de l'add-in RiPart", self.iface.mainWindow())
        
      
        
        self.config.triggered.connect( self.configurePref )
        self.config.setStatusTip(self.tr(u"Ouvre la fenêtre de configuration de l'add-in RIPart."))
        #self.action2.triggered.connect( self.test2 )

        
        self.toolButton = QToolButton()
        self.toolButton.setDefaultAction( self.config) 
        self.toolButton.setPopupMode( QToolButton.InstantPopup )
  
        self.helpMenu= QMenu("Aide")
        self.helpMenu.addAction(self.config)
        self.helpMenu.addAction(self.help)
        self.helpMenu.addAction(self.log)
        self.helpMenu.addAction(self.about)
        self.toolButton2 = QToolButton()
        self.toolButton2.setMenu( self.helpMenu )
        self.toolButton2.setPopupMode( QToolButton.InstantPopup)
        self.toolButton2.setToolButtonStyle (Qt.ToolButtonTextOnly)
        self.toolButton2.setText("Aide")
        
        #self.iface.addToolBarWidget( self.toolButton)
        #self.iface.addToolBarWidget( self.toolButton2)
        
        # self.toolbar.addWidget(self.toolButton)
        self.toolbar.addWidget(self.toolButton2)
        
       
        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&IGN_Ripart'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        self.context= Contexte.getInstance(self,QgsProject)
        if self.context ==None :
            return
      
        if self.context:    
            res=self.context.getConnexionRipart(newLogin=True)   
        
        
    def downloadRemarks(self):
        
        try:
            self.context= Contexte.getInstance(self,QgsProject)            
            importRipart= ImporterRipart(self.context)
            importRipart.doImport()
        except Exception as e:
            self.logger.error(e.message)
            self.context.iface.messageBar(). \
            pushMessage("Erreur",
                         u"Un problème est survenu dans le téléchargement des remarques", \
                         level=2, duration=10)
        

    def connectToRipart(self,context):
        client = Client(context.urlHostRipart, context.login, context.pwd)
        return client        
       
        
    def answerToRemark(self):
        try:
            self.context= Contexte.getInstance(self,QgsProject)  
            reponse = RepondreRipart(self.context)
            reponse.do()
        except Exception as e:
            self.context.iface.messageBar(). \
                pushMessage("Erreur",
                            u"Un problème est survenu lors de l'ajout de la réponse", \
                             level=2, duration=10)
        
        
        
        
    def createRemark(self):
        print "create"
        
    def removeRemarks(self):
        print "remove"
        try:
            self.context= Contexte.getInstance(self,QgsProject)
        
            message=u"Êtes-vous sûr de vouloir supprimer les remarques RIPart de la carte en cours?"
            
            reply= QMessageBox.question(None,'IGN Ripart',message,QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.context.emptyAllRipartLayers()
            else : 
                return
                    
            
        except Exception as e:
            self.context.iface.messageBar(). \
                pushMessage("Erreur",
                            u"Un problème est survenu lors de la suppression des remarques", \
                             level=2, duration=10)
        

    def update(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlgConnexion.show()
        # Run the dialog event loop
        result = self.dlgConnexion.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
        
   
    def configurePref(self):
        print "configure"
    def test1(self):
        print "test1"
    def test2(self):
        print "test2"