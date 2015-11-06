# -*- coding: utf-8 -*-
'''
Created on 27 oct. 2015

@author: AChang-Wailing
'''
import os
import urllib

from core.RipartLoggerCl import RipartLogger 
from PyQt4 import QtGui, uic
from PyQt4.Qt import QDialogButtonBox,QListWidgetItem, QPixmap
from PyQt4.QtCore import *
import core.ConstanteRipart as cst
from core.ClientHelper import ClientHelper
from RipartHelper import RipartHelper
from core.Remarque import Remarque
import core.ConstanteRipart as cst
from core.Theme import Theme
from core.Groupe import Groupe


FORM_CLASS , _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormCreerRemarque_base.ui'))


class FormCreerRemarque(QtGui.QDialog, FORM_CLASS):
    '''
    classdocs
    '''
    
    
    logger=RipartLogger("FormCreerRemarque").getRipartLogger()
    context=None
    
    send=False
    cancel=False
    
    selFileName=None
    
    #dictionnaire des thèmes sélectionnés (key: nom du theme, value: l'objet Theme)
    selectedThemesList={}
    
    #liste des thèmes du profil (objets Theme)
    profilThemesList=[]
    
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
        
        self.groupBoxProfil.setTitle(profil.geogroupe.nom)
        
        data = urllib.urlopen(profil.logo).read()
        pixmap= QPixmap()
        pixmap.loadFromData(data)
        pixmap=pixmap.scaled(41,41,Qt.KeepAspectRatio )   
        self.lblProfilIcon.setPixmap(pixmap)
        
        
        #les noms des thèmes préférés (du fichier de configuration)
        preferredThemes= RipartHelper.load_preferredThemes(self.context.projectDir)
        print preferredThemes
        
        if len(profil.themes)>0:
            #boucle sur tous les thèmes du profil
            for th in profil.themes:
                item= QListWidgetItem()
                item.setData(Qt.DisplayRole,th.groupe.nom)
                
                if th.groupe.nom in preferredThemes:
                    item.setData(Qt.CheckStateRole, Qt.Checked)
                else : 
                    item.setData(Qt.CheckStateRole, Qt.Unchecked)
                    
                self.listWidgetThemes.addItem(item)
                
                #self.profilThemesList[th.groupe.nom]=th
         
        self.profilThemesList=profil.themes   
   
        self.docMaxSize=self.context.client.get_MAX_TAILLE_UPLOAD_FILE()
        
        
    
    def isSingleRemark(self):
        """Indique si l'option de création d'une remarque unique a été choisie.
        """
        return self.radioBtnUnique.isChecked()
    
   
    def getMessage(self):
        return self.textEditMessage.text() 
    
    
    def getSelectedThemes(self):
        """Retourne la liste des thèmes (objets de type THEME) sélectionnés
        """
        selectedThemes=[]
  
        for i in range(0,len(self.listWidgetThemes)) :
            it=self.listWidgetThemes.item(i)
            if it.checkState()==Qt.Checked:
                themeObj=self._getThemeObject(it.text())
                selectedThemes.append(themeObj)
                #selectedThemes.append(self.profilThemesList[it.text()])  
                
        return selectedThemes
    
    
    def _getThemeObject(self,themeName):
        """Retrouve l'objet THEME à partir de son nom
        """
        for th in self.profilThemesList:
            if th.groupe.nom == themeName:
                return th
        return None
                
    def countSelectecTheme(self):
        return len(self.getSelectedThemes())
    
    
    def getAttachedDoc(self):
        if self.checkBoxAttDoc.isChecked():
            return self.selFileName
        else: 
            return ""
    
    def optionWithAttDoc(self):
        return self.checkBoxAttDoc.isChecked()
        
    def optionWithCroquis(self):
        return self.checkBoxJoinCroquis.isChecked()
    
    
    def onListWidgetThemes_click(self):
        print("do ")
        
    
        
    def send(self):
        
        if self.textEditMessage.toPlainText().strip()=="":
            self.lblMessageError.setStyleSheet("QLabel { background-color : #F5A802; font-weight:bold}");
            self.lblMessageError.setText(u"Le message est obligatoire" )
            self.context.iface.messageBar().pushMessage("Attention", u'Le message est obligatoire', level=1, duration=10)
            return   
        
        self.send=True
        self.cancel=False
        
        """tmpRem= Remarque()
            
        tmpRem.setCommentaire(self.textEditMessage.toPlainText())
        
        selectedThemes= self.getSelectedThemes()
        RipartHelper.save_preferredThemes(self.context.projectDir,selectedThemes)
        
        tmpRem.addThemeList(selectedThemes)
        
        tmpRem.addDocument(self.getAttachedDoc())
        
        if self.isSingleRemark():
            #tmpRem.setPosition(position)
            print("single remark")
            
            if self.optionWithCroquis():
                print("with croquis")
                #tmpRem.addCroquis(croquis)
        """
       
        
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
                        
            
            filename = QtGui.QFileDialog.getOpenFileName(self, u'Document à joindre à la remarque', '.',filters)
            if filename!="":
                extension = os.path.splitext(filename)[1]           
                if extension in [".exe",".EXE",".php",".dll"] :
                    message=u"Les fichiers de type '" + extension + u"' ne sont pas autorisées comme pièce-jointe dans le service Ripart."
                    RipartHelper.showMessageBox(message)
                    self.checkBoxAttDoc.setCheckState(Qt.Unchecked)
                    
                elif os.path.getsize(filename)>self.docMaxSize:
                    message=u"Le fichier \"" + filename +\
                           u"\" ne peut être envoyé au service Ripart, car sa taile (" +\
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
        
        