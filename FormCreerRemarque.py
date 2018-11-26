# -*- coding: utf-8 -*-
'''
Created on 27 oct. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
'''

import os
import urllib.request, urllib.parse, urllib.error

from .core.RipartLoggerCl import RipartLogger 

from qgis.PyQt import QtGui, uic, QtWidgets
from PyQt5.Qt import QDialogButtonBox,QListWidgetItem, QPixmap
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QTreeWidgetItem, QDialogButtonBox


from .core import ConstanteRipart as cst
from .core.ClientHelper import ClientHelper
from .core.Remarque import Remarque
from .core import ConstanteRipart as cst
from .core.Theme import Theme
from .core.Groupe import Groupe
from .RipartHelper import RipartHelper
from .core.ThemeAttribut import ThemeAttribut


FORM_CLASS , _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormCreerRemarque_base.ui'))


class FormCreerRemarque(QtWidgets.QDialog, FORM_CLASS):
    """
    Formulaire pour la création d'une nouvelle remarque
    """ 
    logger=RipartLogger("FormCreerRemarque").getRipartLogger()
    context=None
    
    send=False
    cancel=False
    
    #le nom du fichier sélectionné (document joint)
    selFileName=None
    
    #dictionnaire des thèmes sélectionnés (key: nom du theme, value: l'objet Theme)
    selectedThemesList={}
    
    #liste des thèmes du profil (objets Theme)
    profilThemesList=[]
    
    #taille maximale du document joint
    docMaxSize=cst.MAX_TAILLE_UPLOAD_FILE

    def __init__(self, context,croquisCnt, parent=None):
        """Constructor."""
        
        super(FormCreerRemarque, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.context=context
        
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Envoyer")
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")
        
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.send)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        
        self.checkBoxAttDoc.stateChanged.connect(self.openFileDialog)
        
        self.lblDoc.setProperty("visible",False)
        if croquisCnt<2:
            self.radioBtnUnique.setProperty("visible",False)
            self.radioBtnMultiple.setProperty("visible",False)
        else:
            self.radioBtnMultiple.setText(u"Créer "+ str(croquisCnt) + u" remarques distinctes")

        profil= self.context.client.getProfil()
        
        if profil.geogroupe.nom !=None :
            self.groupBoxProfil.setTitle(profil.auteur.nom + " (" + profil.geogroupe.nom + ")")
        else:
            self.groupBoxProfil.setTitle(profil.auteur.nom + u" (Profil par défaut)")
        
        #les noms des thèmes préférés (du fichier de configuration)
        preferredThemes= RipartHelper.load_preferredThemes(self.context.projectDir)
            
        #largeur des colonnes du treeview pour la liste des thèmes et de leurs attributs
        self.treeWidget.setColumnWidth(0,160)
        self.treeWidget.setColumnWidth(1,150)

        
        if len(profil.themes)>0:
            #boucle sur tous les thèmes du profil
            for th in profil.themes:
                #ajout du thème dans le treeview
                thItem= QTreeWidgetItem(self.treeWidget)
                thItem.setText(0,th.groupe.nom)    
                thItem.setText(1,th.groupe.id)
                self.treeWidget.addTopLevelItem(thItem)
                
                #Pour masquer la 2ème colonne (qui contient le groupe id)
                #thItem.setTextColor(1,QtWidgets.QColor(255,255,255,0))
                thItem.setForeground(1, QtGui.QBrush(Qt.white))
                
                if ClientHelper.stringToStringType(th.groupe.nom) in preferredThemes:
                    thItem.setCheckState(0,Qt.Checked)
                    thItem.setExpanded(True)
                else:
                    thItem.setCheckState(0,Qt.Unchecked)
                
                #ajout des attributs du thème
                for att in th.attributs:
                    attLabel = att.nom
                    attType = att.type
                    '''if (len(att.valeurs)>0):
                        attVal = att.valeurs[0]'''
                    attDefaultval = att.defaultval
            
                    if attType == "text": 
                        label = QtWidgets.QLabel(att.nom,self.treeWidget)
                        valeur = QtWidgets.QLineEdit(self.treeWidget)
                        valeur.setText(attDefaultval)
                        txtItem =  QTreeWidgetItem()
                        thItem.addChild(txtItem)
                        self.treeWidget.setItemWidget(txtItem, 0, label)
                        self.treeWidget.setItemWidget(txtItem, 1, valeur)    
                    elif attType == "checkbox" :
                        label = QtWidgets.QLabel(att.nom,self.treeWidget)
                        valeur = QtWidgets.QCheckBox(self.treeWidget)
                        if attDefaultval == 'True' : 
                            valeur.setChecked(True)
                        else:
                            valeur.setChecked(False)     
                        attItem =  QTreeWidgetItem()
                        thItem.addChild(attItem)
                        self.treeWidget.setItemWidget(attItem, 0, label)
                        self.treeWidget.setItemWidget(attItem, 1, valeur)  
                    
                    else:
                        label = QtWidgets.QLabel(att.nom,self.treeWidget)
                        listAtt = QtWidgets.QComboBox(self.treeWidget)
                        attItem =  QtWidgets.QTreeWidgetItem()
                        
                        listAtt.insertItems(0,att.valeurs)
                        
                        thItem.addChild(attItem)
                        self.treeWidget.setItemWidget(attItem, 0, label)
                        self.treeWidget.setItemWidget(attItem, 1, listAtt)  
  
                
        self.profilThemesList=profil.themes   
   
        self.docMaxSize=self.context.client.get_MAX_TAILLE_UPLOAD_FILE()
        
        
    
    def isSingleRemark(self):
        """Indique si l'option de création d'une remarque unique a été choisie.
        """
        return self.radioBtnUnique.isChecked()
    
   
    def getMessage(self):
        """Retourne le message de la remarque
        """
        return self.textEditMessage.text() 
    
    
    def getSelectedThemes(self):
        """Retourne la liste des thèmes (objets de type THEME) sélectionnés
        """
        selectedThemes=[]
        
        root = self.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            thItem = root.child(i)
   
            if thItem.checkState(0)  == Qt.Checked :
                theme = Theme()
                theme.groupe.nom = thItem.text(0)
                theme.groupe.id = thItem.text(1)
                
                for j in range(thItem.childCount()):
                    
                    att = thItem.child(j)
                    label = self.treeWidget.itemWidget(att,0).text()
                    widg = self.treeWidget.itemWidget(att,1)
                    if type(widg) == QtWidgets.QCheckBox :
                        val = str(widg.checkState())
                    elif type(widg) == QtWidgets.QLineEdit :
                        val = widg.text() 
                    else :
                        val = widg.currentText()
      
                    attribut = ThemeAttribut(theme.groupe.nom,ClientHelper.stringToStringType(label), ClientHelper.stringToStringType(val) )
                    theme.attributs.append(attribut)

                selectedThemes.append(theme)               
            
        return selectedThemes
    
    
    def _getThemeObject(self,themeName):
        """Retourne l'objet THEME à partir de son nom
        
        :param themeName: le nom du thème
        :type themeName: string
        
        :return l'objet Theme
        :rtype: Theme
        """
        for th in self.profilThemesList:
            if th.groupe.nom == themeName:
                return th
        return None
                
    def countSelectecTheme(self):
        """Compte et retourne le nombre de thèmes sélectionnés
        
        :return le nombre de thèmes sélectionnés
        :rtype: int
        """
        return len(self.getSelectedThemes())
    
    
    def getAttachedDoc(self):
        """Retourne le nom du fichier sélectionné 
        
        :return nom du fichier sélectionné
        :rtype: string
        """
        if self.checkBoxAttDoc.isChecked():
            return self.selFileName
        else: 
            return ""
    
    def optionWithAttDoc(self):
        """
        :rtype : boolean
        """
        return self.checkBoxAttDoc.isChecked()
        
    def optionWithCroquis(self):
        """
        :rtype : boolean
        """
        return self.checkBoxJoinCroquis.isChecked()
    
    
    def send(self):
        """Envoi de la requête de création au service ripart
        """
        if self.textEditMessage.toPlainText().strip()=="":
            self.lblMessageError.setStyleSheet("QLabel { background-color : #F5A802; font-weight:bold}");
            self.lblMessageError.setText(u"Le message est obligatoire" )
            self.context.iface.messageBar().pushMessage("Attention", u'Le message est obligatoire', level=1, duration=10)
            return   
        
        self.send=True
        self.cancel=False
        
        self.close()
    
        
    def openFileDialog(self):
        if self.checkBoxAttDoc.isChecked() :
          
            filters = "Text files (*.txt);;Images (*.png *.xpm *.jpg)"
            
            filters =  u"All files (*.*);;"+\
                    u"Images (*.BMP;*.JPG;*.GIF;*.JPG2000;*.TIFF;*.ECW;*.PSD);;" +\
                    u"Tracées (*.KML;*.GPX;*.SWG;*.WMF;*.AI);;"+\
                    u"Textes (*.TXT;*.PDF;*.RTF;*.DOC;*.DOCX;*.ODT);;"+\
                    u"Tableurs (*.XML;*.CSV;*XLS;*.XLSX;*.ODS);;"+\
                    u"Base de données (*.MDB;*.MDBX;*.ODB;*.DBF);;"+\
                    u"SIG (*.SHP;*.LYR;*.GDB;*.MXD;*GCM;*.GCR;*.DXF;*.DWG;*.QGS;*.MIF;*MID)"
                        
            
            filename,_ = QtWidgets.QFileDialog.getOpenFileName(self, 'Document à joindre à la remarque', '.',filters)
            if filename!="":
                extension = os.path.splitext(filename)[1]           
                if extension[1:] not in self.context.formats :
                    message=u"Les fichiers de type '" + extension + u"' ne sont pas autorisés comme pièce-jointe dans le service Ripart."
                    RipartHelper.showMessageBox(message)
                    self.checkBoxAttDoc.setCheckState(Qt.Unchecked)
                    
                elif os.path.getsize(filename)>self.docMaxSize:
                    message=u"Le fichier \"" + filename +\
                           u"\" ne peut être envoyé au service Ripart, car sa taille (" +\
                           str(os.path.getsize(filename) / 1000)+\
                           u" Ko) dépasse celle maximalle autorisée (" + str(self.docMaxSize/1000) + u" Ko)"
                            
                    RipartHelper.showMessageBox(message)
                    self.checkBoxAttDoc.setCheckState(Qt.Unchecked)        
                    
                else:
                    self.lblDoc.setProperty("visible",True)
                    self.lblDoc.setText( filename)
                    self.selFileName=filename
            else:
                self.checkBoxAttDoc.setCheckState(Qt.Unchecked)
                self.selFileName=None
            
        else:
            self.lblDoc.setProperty("visible",False)
            self.selFileName=None
            
            
            
    def cancel(self):
        self.cancel=True
        self.send=False
        self.close()
        
        