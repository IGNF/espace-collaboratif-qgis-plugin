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

import PyQt5.QtCore
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QTreeWidgetItem, QDialogButtonBox
from qgis._core import QgsProject
from qgis.core import QgsVectorLayer
from qgis.PyQt import QtCore
from .PluginHelper import PluginHelper
from .core.SQLiteManager import SQLiteManager
from .core import Constantes as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormConfigure_base.ui'))


class FormConfigure(QtWidgets.QDialog, FORM_CLASS):
    """
    Classe de dialogue pour la configuration des préférences de téléchargement des signalements.
    """
    def __init__(self, context, parent=None) -> None:
        """
        Constructeur de la boite "Configuration du plugin Espace Collaboratif".
        Pré-remplissage des champs d'après le fichier de configuration "espaceco.xml"

        NB : appeler dans PluginModule.py, fonction : __configurePlugin
        
        :param context: le contexte
        """
        super(FormConfigure, self).__init__(parent)
        self.setupUi(self)
        self.context = context
        self.setFocus()
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet("QDialog {background-color: rgb(255, 255, 255)}")

        self.buttonBox.button(QDialogButtonBox.Ok).setText("Enregistrer")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.save)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")

        self.lineEditUrl.setText(PluginHelper.load_urlhost(context.projectDir).text)

        login = PluginHelper.load_login(context.projectDir).text
        self.lineEditLogin.setText(login)

        date = PluginHelper.load_XmlTag(context.projectDir, PluginHelper.xml_DateExtraction, "Map").text
        if date is not None:
            date = PluginHelper.formatDate(date)
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
        # Affiche le nom de la couche du polygone d'extraction dans l'item "Zone de travail".
        self.setWorkArea()
        # Affiche les couches sources et champs à mettre en attribut pour les nouveaux croquis
        self.setAttributCroquis()

        proxies = PluginHelper.load_proxy(context.projectDir).text
        self.lineEditProxy.setText(proxies)

        activeCommunityName = PluginHelper.loadActiveCommunityName(context.projectDir).text
        self.lineEditGroupeActif.setText(activeCommunityName)

    def setWorkArea(self) -> None:
        """
        Affiche le nom de la couche du polygone d'extraction dans l'item "Zone de travail".
        À vide par défaut ou si la couche n'existe pas dans le projet.
        """
        self.lineEditWorkArea.setText('')
        workArea = PluginHelper.load_XmlTag(self.context.projectDir, PluginHelper.xml_Zone_extraction, "Map").text
        listLayers = QgsProject.instance().mapLayersByName(workArea)
        if len(listLayers) == 1:
            if listLayers[0].name() == workArea:
                # Si la couche existe toujours dans le projet, la ligne Zone de travail est mise à jour
                # du nom de la couche
                self.lineEditWorkArea.setText(workArea)

    def setAttributCroquis(self) -> None:
        """
        Affiche les couches sources et champs à mettre en attribut pour les nouveaux croquis.
        """
        attCroq = PluginHelper.load_attCroquis(self.context.projectDir)
        if len(attCroq) > 0:
            self.checkBoxAttributs.setChecked(True)
        maplayers = self.context.mapCan.layers()
        topItems = []
        for lay in maplayers:
            if type(lay) is QgsVectorLayer and not lay.name() in PluginHelper.reportSketchLayersName:
                item = QTreeWidgetItem()
                item.setText(0, str(lay.name()))
                inConfig = lay.name() in attCroq
                if inConfig:
                    state = Qt.CheckState.Checked
                else:
                    state = Qt.CheckState.Unchecked
                item.setCheckState(0, state)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
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

    def addSubItems(self, item, layer, attList) -> None:
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
                subItem.setCheckState(0, Qt.CheckState.Checked)
            else:
                subItem.setCheckState(0, Qt.CheckState.Unchecked)
            item.addChild(subItem)

    def onClickItem(self, item, column) -> None:
        """
        Clic sur un item, modifie l'état (coché/décoché) de l'élément parent ou des éléments enfants
        
        :param item: item de l'arbre sur lequel on a cliqué
        :type item: QTreeWidgetItem
        
        :param column: le numéro de colonne
        :type column: int 
        """
        state = item.checkState(column)
        if state == Qt.CheckState.Checked:
            self.checkBoxAttributs.setChecked(True)
        if item.parent() is None:
            childCount = item.childCount()
            for i in range(childCount):
                att = item.child(i)
                att.setCheckState(column, state)
        else:
            parent = item.parent()
            parent.setCheckState(0, self.getParentState(item))

    def getParentState(self, item) -> PyQt5.QtCore.Qt.CheckState:
        """
        :param item: l'élément de l'arbre
        :type item: QTreeWidgetItem

        :return: l'état (coché ou non) du nœud parent
        """
        parent = item.parent()
        childCount = parent.childCount()
        parentState = item.checkState(0)
        if parentState == Qt.CheckState.Checked:
            parentState = Qt.CheckState.Checked
            for i in range(0, childCount):
                if parent.child(i).checkState(0) == Qt.CheckState.Unchecked:
                    parentState = Qt.CheckState.PartiallyChecked
                    break
        else:  
            parentState = Qt.CheckState.Unchecked
            for i in range(0, childCount):
                child = parent.child(i)
                if child.checkState(0) == Qt.CheckState.Checked:
                    parentState = Qt.CheckState.PartiallyChecked
                    break

        return parentState

    def getCheckedTreeItems(self) -> {}:
        """
        :return: les items (attributs) de l'arbre qui sont cochés
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

    def save(self) -> None:
        """
        Sauvegarde la configuration des différents paramètres remplis par l'utilisateur dans le fichier xml.
        """
        # Url, si l'Url a changé, il faut vider la table des tables
        oldUrl = PluginHelper.load_urlhost(self.context.projectDir).text
        newUrl = self.lineEditUrl.text()
        if oldUrl != newUrl:
            SQLiteManager.emptyTable(cst.TABLEOFTABLES)
        PluginHelper.setXmlTagValue(self.context.projectDir, PluginHelper.xml_UrlHost, newUrl, "Serveur")

        # Proxy
        # TODO : revoir le proxy dans la boite de configuration
        if self.checkBoxProxy.isChecked():
            tmp = self.lineEditProxy.text()
            proxies = {'http': tmp, 'https': ''}
        else:
            proxies = {}
        PluginHelper.setXmlTagValue(self.context.projectDir, PluginHelper.xml_proxy, proxies, "Serveur")
        self.context.proxies = proxies

        # date
        if self.checkBoxDate.isChecked():
            d = self.calendarWidget.selectedDate()
            sdate = d.toString('dd/MM/yyyy') + " 00:00:00"
        else:
            sdate = ""
        PluginHelper.setXmlTagValue(self.context.projectDir, PluginHelper.xml_DateExtraction, sdate, "Map")

        # attributs croquis
        PluginHelper.removeAttCroquis(self.context.projectDir)
        if self.checkBoxAttributs.isChecked():
            checkedItems = self.getCheckedTreeItems()
            for calque in checkedItems:
                PluginHelper.setAttributsCroquis(self.context.projectDir, calque, checkedItems[calque])
    
    def keyPressEvent(self, event):
        """
        Pour désactiver la fermeture de la fenêtre si l'utilisateur appuie sur la touche du clavier "Enter" ou "Return"
        """
        key = event.key()
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            pass

    def dateChanged(self):
        """
        Si l'utilisateur choisi une nouvelle date d'extraction alors le nombre de jours est modifié en conséquence.
        """
        d = self.calendarWidget.selectedDate()
        self.spinBox.setValue(self.getCountDays(d))

    def dateMYChanged(self) -> None:
        """
        Si l'utilisateur modifie le mois ou l'année d'extraction alors la date est modifiée dans le calendrier.
        """
        qd = self.calendarWidget.selectedDate()
        m = self.calendarWidget.monthShown()
        y = self.calendarWidget.yearShown()

        date = QDate(y, m, qd.day())
        if not date.isValid():
            maxday = calendar.monthrange(y, m)[1]
            date = QDate(y, m, maxday)
        self.calendarWidget.setSelectedDate(date)

    def getCountDays(self, qdate) -> int:
        """
        Compte le nombre de jours entre la date donnée et la date du jour d'extraction.

        :param qdate: la date de début d'extraction
        :type qdate: QDate

        :return: le nombre de jours décomptés
        """
        date = qdate.toPyDate()
        dt = datetime.now().date()
        countDays = abs((dt-date).days)
        return countDays

    def spinboxChanged(self) -> None:
        """
        Si l'utilisateur change le nombre de jours pour l'extraction alors la date d'extraction est modifiée
        en conséquence dans le calendrier.
        """
        delta = self.spinBox.value()
        now = datetime.now().date()
        calendarDate = now - timedelta(days=delta)
        self.calendarWidget.setSelectedDate(calendarDate)
