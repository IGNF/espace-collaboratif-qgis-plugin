# -*- coding: utf-8 -*-
"""
Created on 20 oct. 2015
Updated on 30 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""

import os.path
from datetime import datetime, timedelta
import calendar

from PyQt5 import QtGui, uic, QtWidgets
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, Qt, QDate
from PyQt5.QtWidgets import QTreeWidgetItem, QDialogButtonBox
from qgis.core import QgsProject, QgsMessageLog, QgsVectorLayer, QgsWkbTypes
from .RipartHelper import RipartHelper
from .Contexte import Contexte

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormConfigurerRipart_base.ui'))


class FormConfigure(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue pour la configuration des préférences de téléchargement des remarques
    """
    #le contexte
    context = None

    def __init__(self, context, parent=None):
        """
        Constructor
        
        Pré-remplissage des champs d'après le fichier de configuration
        
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

        self.context = context
        self.setFocus()

        self.setStyleSheet("QDialog {background-color: rgb(255, 255, 255)}")

        self.buttonBox.button(QDialogButtonBox.Ok).setText("Enregistrer")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.save)

        self.lineEditUrl.setText(RipartHelper.load_urlhost(context.projectDir).text)

        login = RipartHelper.load_login(context.projectDir).text
        self.lineEditLogin.setText(login)
        if login != "" and login is not None:
            self.checkBoxLogin.setChecked(True)

        pagination = RipartHelper.load_ripartXmlTag(context.projectDir, RipartHelper.xml_Pagination, "Map").text
        if pagination == "" or pagination is None:
            pagination = 100
        else:
            self.checkBoxPagination.setChecked(True)
        self.spinBoxPagination.setValue(int(pagination))

        date = RipartHelper.load_ripartXmlTag(context.projectDir, RipartHelper.xml_DateExtraction, "Map").text
        if date is not None:
            date = RipartHelper.formatDate(date)
            dt = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            self.checkBoxDate.setChecked(True)
        else:
            dt = datetime.now()

        qdate = QDate(dt.year, dt.month, dt.day)
        self.calendarWidget.setSelectedDate(qdate)
        dateNow = datetime.now()
        cntDays = abs((dateNow - dt).days)

        self.dateMY = False
        self.calendarWidget.selectionChanged.connect(self.dateChanged)
        self.calendarWidget.currentPageChanged.connect(self.dateMYChanged)

        self.spinBox.setValue(cntDays)
        self.spinBox.valueChanged.connect(self.spinboxChanged)

        workArea = RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_Zone_extraction, "Map").text
        self.lineEditWorkArea.setText(workArea)

        # self.setComboBoxFilter()

        groupFilter = RipartHelper.load_ripartXmlTag(context.projectDir, RipartHelper.xml_Group, "Map").text
        if groupFilter is not None and groupFilter == "true":
            self.checkBoxGroup.setChecked(True)
        if self.context.profil is not None:
            self.lblGroup.setText(self.context.profil.geogroup.name)

        self.setAttributCroquis()

        proxy = RipartHelper.load_proxy(context.projectDir).text
        self.lineEditProxy.setText(proxy)

        groupeactif = RipartHelper.load_groupeactif(context.projectDir).text
        self.lineEditGroupeActif.setText(groupeactif)

    def setComboBoxFilter(self):
        """
        Set de la liste des couches de type "polygone" susceptibles d'être utilisées comme zone d'extraction
        """
        polyLayers = self.context.getMapPolygonLayers()

        polyList = [val for key, val in polyLayers.items() if val != RipartHelper.nom_Calque_Croquis_Polygone]
        self.comboBoxFiltre.clear()
        self.comboBoxFiltre.addItems(polyList)

        zone = RipartHelper.load_ripartXmlTag(self.context.projectDir, RipartHelper.xml_Zone_extraction, "Map").text

        index = self.comboBoxFiltre.findText(zone, Qt.MatchCaseSensitive)
        if index >= 0:
            self.comboBoxFiltre.setCurrentIndex(index)
            self.checkBoxFiltre.setChecked(True)
        else:
            self.checkBoxFiltre.setChecked(False)

    def setAttributCroquis(self):
        """
        Set des atttributs des croquis dans le treeWidget
        """
        attCroq = RipartHelper.load_attCroquis(self.context.projectDir)
        if len(attCroq) > 0:
            self.checkBoxAttributs.setChecked(True)

        maplayers = self.context.mapCan.layers()

        topItems = []

        for lay in maplayers:
            if type(lay) is QgsVectorLayer and not lay.name() in RipartHelper.croquis_layers_name:
                item = QTreeWidgetItem()
                item.setText(0, str(lay.name()))
                inConfig = lay.name() in attCroq
                if inConfig:
                    state = Qt.Checked
                else:
                    state = Qt.Unchecked
                item.setCheckState(0, state) # Qt.Unchecked/Qt.Checked
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                topItems.append(item)

                if inConfig:
                    attList = attCroq[lay.name()]
                else:
                    attList = None

                self.addSubItems(item, lay, attList)

                # set parent state (checked or partiallyChecked)
                if item.childCount() > 0:
                    pstate = self.getParentState(item.child(0))
                    item.setCheckState(0, pstate)

        self.treeWidget.insertTopLevelItems(0, topItems)
        self.treeWidget.itemClicked.connect(self.onClickItem)

    def addSubItems(self, item, layer, attList):
        """
        Adds subitems to the tree view
        The subitems are the attributes of the layers 
        
        :param item: l'item de l'arbre (calque) auquel il faut ajouter les sous-items (attributs)
        :type item: QTreeWidgetItem
        
        :param layer: le calque
        :type layer: QgsVectorlayer
        
        :param attList: un dictionnaire des attributs à ajouter (key:nom du calque, value:liste des attributs du calque)
        :type attList: dictionary 
        """
        fieldNames = [field.name() for field in layer.fields()]

        for f in fieldNames:
            subItem = QTreeWidgetItem()
            subItem.setText(0, str(f))

            if attList is not None and f in attList:
                subItem.setCheckState(0, Qt.Checked)
            else:
                subItem.setCheckState(0, Qt.Unchecked)
            item.addChild(subItem)

    def onClickItem(self, item, column):
        """Clic sur un item =>set de l'état de l'élément parent ou des éléments enfants
        
        :param item: item de l'arbre sur lequel on a cliqué
        :type item: QTreeWidgetItem
        
        :param column: le no de colonne
        :type column: int 
        """
        state = item.checkState(column)
        if state == Qt.Checked:
            self.checkBoxAttributs.setChecked(True)
        if item.parent() is None:
            childCount = item.childCount()
            for i in range(childCount):
                att = item.child(i)
                att.setCheckState(column, state)
        else:
            parent = item.parent()
            parent.setCheckState(0, self.getParentState(item))

    def getParentState(self, item):
        """Retourne l'état (coché ou non) du noeud parent
        
        :param item: l'élément de l'arbre
        :type item: 
        """
        parent = item.parent()
        childCount = parent.childCount()
        pstate = item.checkState(0)
        if pstate == Qt.Checked:
            pstate = Qt.Checked
            for i in range(0, childCount):
                if parent.child(i).checkState(0) == Qt.Unchecked:
                    pstate = Qt.PartiallyChecked
                    break
        else:  
            pstate = Qt.Unchecked
            for i in range(0, childCount):
                child = parent.child(i)
                if child.checkState(0) == Qt.Checked:
                    pstate = Qt.PartiallyChecked
                    break

        return pstate

    def getCheckedTreeItems(self):
        """
        Retourne les items de l'arbre des attributs qui sont cochés
        """
        tree = self.treeWidget
        checkedItems = {}
        for i in range(0, self.treeWidget.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item.checkState(0):
                checkedItems[item.text(0)] = []
                for j in range(0, item.childCount()):
                    subitem = item.child(j)
                    if subitem.checkState(0):
                        checkedItems[item.text(0)].append(subitem.text(0))
        return checkedItems

    def save(self):
        """
        Sauvegarde la configuration des différents paramètres dans le fichier xml
        """
        
        # Url
        RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_UrlHost, self.lineEditUrl.text(), "Serveur")
        
        # login
        if self.checkBoxLogin.isChecked():
            login = self.lineEditLogin.text()
        else:
            login = ""
        RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_Login, login, "Serveur")

        # pagination
        if self.checkBoxPagination.isChecked():
            pag = str(self.spinBoxPagination.value())
        else:
            pag = ""
        RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_Pagination, pag, "Map")

        # date
        if self.checkBoxDate.isChecked():
            d = self.calendarWidget.selectedDate()
            sdate = d.toString('dd/MM/yyyy') + " 00:00:00"
        else:
            sdate = ""

        RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_DateExtraction, sdate, "Map")

        # zone de filtrage
        if self.checkBoxFiltre.isChecked():
            filtre = self.comboBoxFiltre.currentText()
        else:
            filtre = ""
        
        RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_Zone_extraction, filtre, "Map")

        # filtre groupe
        if self.checkBoxGroup.isChecked():
            groupFilter = "true"
        else:
            groupFilter = ""

        RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_Group, groupFilter, "Map")

        # attributs croquis
        RipartHelper.removeAttCroquis(self.context.projectDir)
        if self.checkBoxAttributs.isChecked():
            checkedItems = self.getCheckedTreeItems()
            for calque in checkedItems:
                RipartHelper.setAttributsCroquis(self.context.projectDir, calque, checkedItems[calque])

        # Groupe actif
        RipartHelper.setXmlTagValue(self.context.projectDir, RipartHelper.xml_GroupeActif, self.lineEditGroupeActif.text(), "Serveur")
    
    def keyPressEvent(self, event):
        """
        Pour désactiver la fermeture de la fenêtre lors d'un clic sur "Enter"
        """
        key = event.key()
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            pass

    def dateChanged(self):
        """Action lors d'un changement de date
        =>Modification du nombre de jours
       """
        self.dateSelected = True
        d = self.calendarWidget.selectedDate()
        self.spinBox.setValue(self.getCountDays(d))

    def dateMYChanged(self):
        """Action lors d'une modification du mois ou de l'année
        """
        self.dateMYChanged = True
        qd = self.calendarWidget.selectedDate()
        m = self.calendarWidget.monthShown()
        y = self.calendarWidget.yearShown()

        date = QDate(y, m, qd.day())
        if not date.isValid():
            maxday = calendar.monthrange(y, m)[1]
            date = QDate(y, m, maxday)
        self.calendarWidget.setSelectedDate(date)

    def getCountDays(self, qdate):
        """Compte le nombre de jours entre la date donnée et la date d'aujourd'hui
        :param qdate: la date 
        :type qdate: QDate
        """
        date = qdate.toPyDate()
        dt = datetime.now().date()
        cntDays = abs((dt-date).days)
        return cntDays

    def spinboxChanged(self):
        """Action lors d'un changement du nb de jours
           =>Modification de la date
        """
        delta = self.spinBox.value()
        now = datetime.now().date()
        calendarDate = now - timedelta(days=delta)
        self.calendarWidget.setSelectedDate(calendarDate)
