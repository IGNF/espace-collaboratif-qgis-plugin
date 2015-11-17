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

import os.path
from core.RipartLoggerCl import RipartLogger


from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL, Qt
from PyQt4 import QtGui, uic
from PyQt4.QtGui import  QAction, QIcon, QMenu,QMessageBox,QToolButton,QApplication
from qgis.core import *
from qgis._core import QgsProject,  QgsMessageLog
import ConfigParser

# Initialize Qt resources from file resources.py
import resources

# modules ripart
from FormConnexion_dialog import FormConnexionDialog
from FormInfo import FormInfo
from FormConfigure import FormConfigure
from Contexte import Contexte
from core.Client import Client
from ImporterRipart import ImporterRipart
from FormRepondre import FormRepondreDialog
from RepondreRipart import RepondreRipart
from CreerRipart import CreerRipart
import core.ConstanteRipart as cst
from Magicwand import Magicwand



class RipartPlugin:
    """QGIS Plugin Implementation."""
    
    context=None
    logger= None
    ripartLogger=None

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.ripartLogger=RipartLogger("RipartPlugin")
        self.logger=self.ripartLogger.getRipartLogger()
        
        
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
        
      
        # Create the dialog (after translation) and keep reference
        self.dlgConnexion = FormConnexionDialog()
        
  
        # La toolbar du plugin
        self.actions = []
        self.menu = self.tr(u'&IGN_Ripart')

        self.toolbar = self.iface.addToolBar(u'RipartPlugin')
        self.toolbar.setObjectName(u'RipartPlugin')
        
 

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
        
        icon_path = ':/plugins/RipartPlugin/images/viewRem.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Voir la remarque'),
            callback=self.viewRem,
            status_tip=self.tr(u'Voir la remarque'),
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
            text=self.tr(u'Créer une nouvelle remarque'),
            callback=self.createRemark,
            status_tip=self.tr(u'Créer une nouvelle remarque'),
            parent=self.iface.mainWindow())
        
        icon_path = ':/plugins/RipartPlugin/images/cleaning.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Supprimer les remarques de la carte en cours'),
            callback=self.removeRemarks,
            status_tip=self.tr(u'Supprimer les remarques de la carte en cours'),
            parent=self.iface.mainWindow())
               
        icon_path = ':/plugins/RipartPlugin/images/magicwand.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Voir les objets associés'),
            callback=self.magicwand,
            status_tip=self.tr(u'Voir les objets associés'),
            parent=self.iface.mainWindow())
           
        self.config = QAction(QIcon(":/plugins/RipartPlugin/images/config.png"), u"Configurer le plugin RIPart", self.iface.mainWindow())
        self.help = QAction(QIcon(":/plugins/RipartPlugin/images/Book.png"), "Ouvrir le manuel utilisateur du plugin RIPart", self.iface.mainWindow())
        self.log= QAction(QIcon(":/plugins/RipartPlugin/images/Log.png"), "Ouvrir le fichier de log du plugin RIPart", self.iface.mainWindow())
        self.about = QAction(QIcon(":/plugins/RipartPlugin/images/About.png"), "A propos du plugin RIPart", self.iface.mainWindow())
             
        self.config.triggered.connect( self.configurePref )
        self.config.setStatusTip(self.tr(u"Ouvre la fenêtre de configuration de l'add-in RIPart."))
        
        self.about.triggered.connect( self.ripAbout)
        self.help.triggered.connect(self.showHelp)
        self.log.triggered.connect(self.showLog)

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
        

        self.toolbar.addWidget(self.toolButton2)
        
       
        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&IGN_Ripart'),
                action)
            self.iface.removeToolBarIcon(action)



    def run(self):
        """Fenêtre de connexion"""
        
        self.context= Contexte.getInstance(self,QgsProject)
        if self.context ==None :
            return
      
        if self.context:    
            res=self.context.getConnexionRipart(newLogin=True)  

        
        
    def downloadRemarks(self):
        """Downloads remarks
        """
        try:
            self.context= Contexte.getInstance(self,QgsProject)   
            if self.context ==None :
                return    
                 
            importRipart= ImporterRipart(self.context)
            importRipart.doImport()
        except Exception as e:
            self.logger.error(e.message)
            self.context.iface.messageBar(). \
            pushMessage("Erreur",
                         u"Un problème est survenu dans le téléchargement des remarques", \
                         level=2, duration=10)
            QApplication.setOverrideCursor(Qt.ArrowCursor)



    def connectToRipart(self,context):
        """Connection to the ripart service 
        """
        client = Client(context.urlHostRipart, context.login, context.pwd)
        return client        
       
        
    def answerToRemark(self):
        """Answer to a remark
        """
        try:
            self.context= Contexte.getInstance(self,QgsProject)  
            if self.context ==None :
                return 
            reponse = RepondreRipart(self.context)
            reponse.do()
        except Exception as e:
            self.context.iface.messageBar(). \
                pushMessage("Erreur",
                            u"Un problème est survenu lors de l'ajout de la réponse", \
                             level=2, duration=10)
        
        
        
        
    def createRemark(self):
        """Create a new remark
        """
        try:
            self.context= Contexte.getInstance(self,QgsProject)  
            if self.context ==None :
                return 
            create = CreerRipart(self.context)
            create.do()
        except Exception as e:
            self.context.iface.messageBar(). \
                pushMessage("Erreur",
                            u"Un problème est survenu lors de la création de la remarque", \
                             level=2, duration=10)
        
    def removeRemarks(self):
        """Remove all remarks from current map
        (empty the tables from ripart table of the sqlite DB)
        """
        
        try:
            self.context= Contexte.getInstance(self,QgsProject)
            if self.context ==None :
                return 
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
        

    """def update(self):
        
        # show the dialog
        self.dlgConnexion.show()
        # Run the dialog event loop
        result = self.dlgConnexion.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
     """   
   
    def configurePref(self):
        """Lance la fenêtre de configuration des préférences 
        """
        
        try:
            self.context= Contexte.getInstance(self,QgsProject)   
            if self.context ==None :
                return 
            
            self.context.checkConfigFile()    
            self.dlgConfigure=FormConfigure(context=self.context)
              
            self.dlgConfigure.exec_()
            
        except Exception as e:
            self.logger.error(e.message)
            self.context.iface.messageBar(). \
            pushMessage("Erreur",
                         u"Un problème est survenu dans le chargement de la configuration."+e.message, \
                        level=2, duration=10)
                     
        
    def magicwand(self):
        """Sélectionne la/les remarque(s) associée(s) au(x) croquis sélectionnés 
          ou le/les croquis associé(s) à la remarque sélectionnée.
          On ne peut pas sélectionnner des remarques et des croquis (soit remarques, soit croquis)  
        """
        try:
            self.context= Contexte.getInstance(self,QgsProject)  
            magicw=Magicwand(self.context)
            magicw.selectRipartObjects()
           
        except Exception as e:
            self.logger.error("magicWand "+ e.message)
    
    
    def viewRem(self):
        """Visualisation de la remarque  (message, réponses et statut)
        """  
        try:
            self.context= Contexte.getInstance(self,QgsProject)  
            if self.context ==None :
                return 
           
            reponse = RepondreRipart(self.context)
            self.formView=reponse.do(isView=True)
                       
        except Exception as e:
            self.logger.error("viewRem "+ e.message)
            self.context.iface.messageBar(). \
                pushMessage("Erreur",
                            u"Un problème est survenu", \
                             level=2, duration=10)
        
        
    
    def ripAbout(self):
        """Montre la fenêtre "about" avec les informations de version du plugin 
        """
        version='0.'
        date='2015'
        
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),'metadata.txt'))
     
        parser = ConfigParser.ConfigParser()
        parser.optionxform = str
        parser.read(file_path)
        if parser.has_section('general'):
            try:
                version=parser.get('general','version')
                date=parser.get('general','date')
            except Exception as e:
                self.logger.error("No version/date in metadata")
       
        
        dlgInfo=FormInfo()
        dlgInfo.textInfo.setText(u"<b>RIPart</b>")
        dlgInfo.textInfo.append(u"<br/>Plugin intégrant les services RIPart")
        dlgInfo.textInfo.append(u"<br/>Version: "+ version )
        dlgInfo.textInfo.append(u"\u00A9 IGN - " + date )
       
        dlgInfo.exec_()
  
  
  
    def showHelp(self):
        """Ouvre le document d'aide utilisateur
        """
        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),"files",cst.helpFile))
        
        os.startfile(file_path)
        
        
        
    def showLog(self):
        """Ouvre le dernier fichier de log
        """
        logpath=self.ripartLogger.getLogpath()
        if logpath!=None:
            os.startfile(logpath)
  
  
  