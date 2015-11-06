# -*- coding: utf-8 -*-
'''
Created on 20 oct. 2015

@author: AChang-Wailing
'''
import os

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox

from PyQt4.QtCore import *
import FormConfigurerRipart_base

from RipartHelper import RipartHelper
from datetime import datetime
from PyQt4.Qt import QTreeWidgetItem, QDialogButtonBox
import calendar

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormConfigurerRipart_base.ui'))


class FormConfigure(QtGui.QDialog, FORM_CLASS):
    """
    Dialogue pour la configuration des préférences de téléchargement des remarques
    """
    
    #le contexte
    context=None

    def __init__(self, context, parent=None):
        """
        Constructor
        
        :param context le contexte 
        :type context Contexte
        
        
        """  
        super(FormConfigure, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        # Save reference to the QGIS interface
        
        self.context=context    
        self.setFocus()
              
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Enregistrer")
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")
        
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.save)
  
        #pré-remplissage des champs d'après le fichier de configuration
        self.lineEditUrl.setText(RipartHelper.load_urlhost(context.projectDir).text)
        
        login=RipartHelper.load_login(context.projectDir).text
        
        self.lineEditLogin.setText(login)
        if login!="" and login!= None:
            self.checkBoxLogin.setChecked(True)
        
        pagination= RipartHelper.load_ripartXmlTag(context.projectDir, RipartHelper.xml_Pagination,"Map").text
        if pagination=="" or pagination ==None:
            pagination =100
            
        else:
            self.checkBoxPagination.setChecked(True)
        self.spinBoxPagination.setValue(int(pagination))

        
        date=RipartHelper.load_ripartXmlTag(context.projectDir, RipartHelper.xml_DateExtraction,"Map").text
        if date !=None :
            date = RipartHelper.formatDate(date)
            dt= datetime.strptime(date,'%Y-%m-%d %H:%M:%S')
            self.checkBoxDate.setChecked(True)
        else:
            dt= datetime.now()
            
        qdate= QDate(dt.year,dt.month,dt.day)
        self.calendarWidget.setSelectedDate(qdate)    
        dateNow= datetime.now()
        cntDays= abs((dateNow - dt).days)
        
        self.dateMY=False
        self.calendarWidget.selectionChanged.connect(self.dateChanged)
        self.calendarWidget.currentPageChanged.connect(self.dateMYChanged)
          
        self.spinBox.setValue(cntDays)
        
        self.setComboBoxFilter()
         
        groupFilter=RipartHelper.load_ripartXmlTag(context.projectDir, RipartHelper.xml_Group,"Map").text
        if groupFilter!=None and groupFilter=="true":
            self.checkBoxGroup.setChecked(True)
        if self.context.profil!=None:
            self.lblGroup.setText(self.context.profil.geogroupe.nom)
                
        self.setAttributCroquis()
        
        
    
    def setComboBoxFilter(self):
        '''
        Set de la liste des couches de type "polygone" susceptibles d'être utilisées comme zone d'extraction
        '''
        polyLayers=self.context.getMapPolygonLayers()
        
        polyList=[val for key,val in polyLayers.iteritems() if val!=RipartHelper.nom_Calque_Croquis_Polygone]
        self.comboBoxFiltre.clear()
        self.comboBoxFiltre.addItems(polyList)
        
        zone=RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_Zone_extraction,"Map").text
        
        index = self.comboBoxFiltre.findText(zone, Qt.MatchCaseSensitive)
        if index >= 0:
            self.comboBoxFiltre.setCurrentIndex(index)
            self.checkBoxFiltre.setChecked(True)
        else :
            self.checkBoxFiltre.setChecked(False)
    
    
    """def setZoneFilter(self,zone):    
        index = self.comboBoxFiltre.findText(zone, Qt.MatchCaseSensitive)
        if index >= 0:
            self.comboBoxFiltre.setCurrentIndex(index)
            self.checkBoxFiltre.setChecked(True)
        else :
            self.checkBoxFiltre.setChecked(False)
            
        
    def initComboZoneFilter(self):
        '''
        Initialisation de la liste des couches de type "polygone" susceptibles d'être utilisées comme zone d'extraction
        '''
        polyLayers=self.context.getMapPolygonLayers()
        
        polyList=[val for key,val in polyLayers.iteritems() if val!=RipartHelper.nom_Calque_Croquis_Polygone]
        self.comboBoxFiltre.clear()
        self.comboBoxFiltre.addItems(polyList)
        
        zone=RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_Zone_extraction,"Map").text
        
        self.setZoneFilter(zone)
    """    
  
        
    def setAttributCroquis(self):
        """
        Set des atttributs des croquis dans le treeWidget
        """
        attCroq=RipartHelper.load_attCroquis(self.context.projectDir)
        if len(attCroq)>0:
            self.checkBoxAttributs.setChecked(True)
       
        maplayers= self.context.mapCan.layers()
        
        ripartLayers=[RipartHelper.nom_Calque_Remarque,
                     RipartHelper.nom_Calque_Croquis_Ligne,
                     RipartHelper.nom_Calque_Croquis_Fleche,
                     RipartHelper.nom_Calque_Croquis_Point,
                     RipartHelper.nom_Calque_Croquis_Polygone,
                     RipartHelper.nom_Calque_Croquis_Texte]
        
        topItems=[]
        
        for lay in maplayers :
            if not lay.name() in ripartLayers:
                item = QTreeWidgetItem()
                item.setText(0,unicode (lay.name()))
                inConfig=lay.name() in attCroq
                if inConfig:
                    state=Qt.Checked
                else:
                    state=Qt.Unchecked
                item.setCheckState(0,state)    #Qt.Unchecked/Qt.Checked
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable) 
                topItems.append(item)
            
                if inConfig:
                    attList=attCroq[lay.name()]
                else : 
                    attList=None
                    
                self.addSubItems(item,lay,attList)
                
                #set parent state (checked or partiallyChecked)
                if (item.childCount()>0):
                    pstate=self.getParentState(item.child(0))
                    item.setCheckState(0,pstate)
       
        self.treeWidget.insertTopLevelItems(0, topItems)
        
        self.connect(self.treeWidget, SIGNAL("itemClicked(QTreeWidgetItem*, int)"),self.onClickItem)
    
    
    def addSubItems(self,item,layer,attList):
        """
        Adds subitems to the tree view
        The subitems are the attributes of the layers 
        
        :param item l'item de l'arbre (calque) auquel il faut ajouter les sous-items (attributs)
        """
        fieldNames = [field.name() for field in layer.pendingFields() ]
        
        for f in fieldNames:
            subItem=  QTreeWidgetItem()
            subItem.setText(0,unicode(f))
            
            if attList !=None and f in attList: 
                subItem.setCheckState(0,Qt.Checked)
            else:
                subItem.setCheckState(0,Qt.Unchecked)
            item.addChild(subItem)
            
    
    def onClickItem (self, item, column):
        """Clic sur un item =>set de l'état de l'élémént parent ou des éléments enfants
        """
        print (item.text(column))
        state=item.checkState(column)
        if state==Qt.Checked :
            self.checkBoxAttributs.setChecked(True)
        if item.parent()==None:
            childCount=item.childCount()
            for i in range(childCount):
                att=item.child(i)
                att.setCheckState(column,state)
        else:
            parent =item.parent()
            parent.setCheckState(0,self.getParentState(item))
           
    
    
    def getParentState(self,item):
        """
        """
        parent =item.parent()
        childCount=parent.childCount()
        pstate= item.checkState(0)
        if pstate==Qt.Checked:
            pstate= Qt.Checked
            for i in range(0,childCount):
                if parent.child(i).checkState(0)==Qt.Unchecked:
                    pstate=Qt.PartiallyChecked
                    break
                    
        else:  
            pstate= Qt.Unchecked
            for i in range(0,childCount):
                child=parent.child(i)
                if child.checkState(0)==Qt.Checked:
                    pstate=Qt.PartiallyChecked
                    break
        
        return pstate
              
        
    
    def getCheckedTreeItems(self):
        tree=self.treeWidget
        checkedItems={}
        for i in range(0,self.treeWidget.topLevelItemCount()):
            
            item= tree.topLevelItem(i)
            if item.checkState(0):
                checkedItems[item.text(0)]=[]
                for j in range (0,item.childCount() ):
                    subitem=item.child(j)
                    if subitem.checkState(0):
                        checkedItems[item.text(0)].append(subitem.text(0))
                        
        
        return checkedItems
        
    
    def save(self):
        errMessage=""
        
        #Url
        RipartHelper.setXmlTagValue(self.context.projectDir,RipartHelper.xml_UrlHost,self.lineEditUrl.text(),"Serveur")
        
        #login      
        if self.checkBoxLogin.isChecked():
            login=self.lineEditLogin.text()
        else:
            login=""
        RipartHelper.setXmlTagValue(self.context.projectDir,RipartHelper.xml_Login,login,"Serveur")
        
        #pagination
        if self.checkBoxPagination.isChecked():
            pag= str(self.spinBoxPagination.value())
        else :
            pag= ""
        RipartHelper.setXmlTagValue(self.context.projectDir,RipartHelper.xml_Pagination,pag,"Map")
                
        #date
        if self.checkBoxDate.isChecked():
            d=self.calendarWidget.selectedDate()
            sdate=d.toString('dd/MM/yyyy') + " 00:00:00"         
        else : 
            sdate=""
            
        RipartHelper.setXmlTagValue(self.context.projectDir,RipartHelper.xml_DateExtraction,sdate,"Map")
       
        
        #zone de filtrage
        if self.checkBoxFiltre.isChecked():
            filtre=self.comboBoxFiltre.currentText()
        else :
            filtre =""
        
        RipartHelper.setXmlTagValue(self.context.projectDir,RipartHelper.xml_Zone_extraction,filtre,"Map")
        
        
        #filtre groupe
        if self.checkBoxGroup.isChecked():
            groupFilter="true"
        else:
            groupFilter=""
            
        RipartHelper.setXmlTagValue(self.context.projectDir,RipartHelper.xml_Group,groupFilter,"Map")
        
        #attributs croquis
        #RipartHelper.setXmlTagValue(self.context.projectDir,RipartHelper.xml_AttributsCroquis,"","Map")
        RipartHelper.removeAttCroquis(self.context.projectDir)
        if self.checkBoxAttributs.isChecked():
            checkedItems=self.getCheckedTreeItems()
            for calque in checkedItems:
                RipartHelper.setAttributsCroquis(self.context.projectDir, calque,checkedItems[calque])
        else:
            print "att not checked"
    
    def keyPressEvent(self, event):
        key = event.key()
        if key ==Qt.Key_Return or key ==Qt.Key_Enter:
            #print"do nothing"
            pass
    
    def dateChanged(self):
        print "date changed"
        self.dateSelected=True
        d=self.calendarWidget.selectedDate()
       
        #if d!=None:
        #    sdate=d.toString('dd/MM/yyyy') + " 00:00:00"  
        
    
        self.spinBox.setValue(self.getCountDays(d))
        
    def dateMYChanged(self):
        self.dateMYChanged=True
        qd=self.calendarWidget.selectedDate()
        m=self.calendarWidget.monthShown()
        y=self.calendarWidget.yearShown()
        
        date = QDate(y,m,qd.day())
        if not date.isValid():
            maxday=calendar.monthrange(y,m)[1]
            date =QDate(y,m,maxday)
        print date.toString('dd/MM/yyyy') 
        self.calendarWidget.setSelectedDate(date)
        
        
    def getCountDays(self,qdate):
        """
        """
        date= qdate.toPyDate()
        dt= datetime.now().date()
        cntDays= abs((dt- date).days)
        
        return cntDays