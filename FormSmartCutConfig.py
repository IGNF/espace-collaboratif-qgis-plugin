# -*- coding: utf-8 -*-
"""
FormSmartCutConfig - Configuration dialog for Smart Cut tool

Dialog to configure which attributes should remain unique when cutting polygons.

Created on January 7, 2026
@author: GitHub Copilot
"""

from PyQt5.QtWidgets import QDialog, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt
from qgis.core import QgsVectorLayer, QgsWkbTypes
from .FormSmartCutConfig_base import Ui_DialogSmartCutConfig
from .core.SmartCutHelper import SmartCutHelper
from .core.PluginLogger import PluginLogger


class FormSmartCutConfig(QDialog, Ui_DialogSmartCutConfig):
    """
    Configuration dialog for the Smart Cut tool.
    Allows users to specify which attributes should be unique.
    """
    
    def __init__(self, context, parent=None):
        """
        Initialize the configuration dialog.
        
        :param context: Plugin context
        :type context: Contexte
        :param parent: Parent widget
        :type parent: QWidget
        """
        super(FormSmartCutConfig, self).__init__(parent)
        self.setupUi(self)
        
        self.__context = context
        self.__logger = PluginLogger("FormSmartCutConfig").getPluginLogger()
        
        self.__connectSignals()
        self.__loadSettings()
        self.__loadFromActiveLayer()
    
    def __connectSignals(self):
        """
        Connect UI signals to slots.
        """
        self.btnRefreshLayer.clicked.connect(self.__loadFromActiveLayer)
        self.btnAddToUnique.clicked.connect(self.__addToUnique)
        self.btnRemoveFromUnique.clicked.connect(self.__removeFromUnique)
    
    def __loadSettings(self):
        """
        Load unique attributes from settings.
        """
        unique_attrs = SmartCutHelper.getUniqueAttributes()
        
        self.listUniqueAttrs.clear()
        for attr in unique_attrs:
            self.listUniqueAttrs.addItem(attr)
        
        self.__logger.info(f"Chargement de {len(unique_attrs)} attributs uniques depuis les paramètres")
    
    def __loadFromActiveLayer(self):
        """
        Load field names from the active layer.
        """
        self.listAvailableFields.clear()
        
        layer = self.__context.iface.activeLayer()
        
        if not layer or not isinstance(layer, QgsVectorLayer):
            self.labelLayerInfo.setText("<i>Aucune couche vectorielle active</i>")
            return
        
        if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            self.labelLayerInfo.setText(f"Couche: <b>{layer.name()}</b> <i>(pas une couche de polygones)</i>")
            return
        
        self.labelLayerInfo.setText(f"Couche: <b>{layer.name()}</b>")
        
        # Load fields
        field_names = SmartCutHelper.getLayerFieldNames(layer)
        for field_name in field_names:
            self.listAvailableFields.addItem(field_name)
        
        self.__logger.info(f"Chargement de {len(field_names)} champs depuis la couche '{layer.name()}'")
    
    def __addToUnique(self):
        """
        Add selected fields from available list to unique attributes list.
        """
        selected_items = self.listAvailableFields.selectedItems()
        
        if not selected_items:
            QMessageBox.information(
                self,
                "Aucune sélection",
                "Veuillez sélectionner au moins un attribut à ajouter."
            )
            return
        
        # Get current unique attributes
        existing_attrs = set()
        for i in range(self.listUniqueAttrs.count()):
            existing_attrs.add(self.listUniqueAttrs.item(i).text())
        
        # Add new ones
        added_count = 0
        for item in selected_items:
            field_name = item.text()
            if field_name not in existing_attrs:
                self.listUniqueAttrs.addItem(field_name)
                existing_attrs.add(field_name)
                added_count += 1
        
        if added_count > 0:
            self.__logger.info(f"{added_count} attribut(s) ajouté(s) aux attributs uniques")
        else:
            QMessageBox.information(
                self,
                "Déjà présent",
                "Les attributs sélectionnés sont déjà dans la liste des attributs uniques."
            )
    
    def __removeFromUnique(self):
        """
        Remove selected attributes from unique list.
        """
        selected_items = self.listUniqueAttrs.selectedItems()
        
        if not selected_items:
            QMessageBox.information(
                self,
                "Aucune sélection",
                "Veuillez sélectionner au moins un attribut à retirer."
            )
            return
        
        # Remove items
        for item in selected_items:
            row = self.listUniqueAttrs.row(item)
            self.listUniqueAttrs.takeItem(row)
        
        self.__logger.info(f"{len(selected_items)} attribut(s) retiré(s) des attributs uniques")
    
    def accept(self):
        """
        Save settings and close dialog.
        """
        # Collect unique attributes
        unique_attrs = []
        for i in range(self.listUniqueAttrs.count()):
            unique_attrs.append(self.listUniqueAttrs.item(i).text())
        
        if not unique_attrs:
            reply = QMessageBox.question(
                self,
                "Aucun attribut unique",
                "Vous n'avez sélectionné aucun attribut unique.\n"
                "L'outil de découpe traitera tous les attributs de manière égale.\n\n"
                "Continuer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Save to settings
        SmartCutHelper.setUniqueAttributes(unique_attrs)
        
        self.__logger.info(f"Configuration sauvegardée: {len(unique_attrs)} attribut(s) unique(s)")
        
        # Show success message
        QMessageBox.information(
            self,
            "Configuration sauvegardée",
            f"Les paramètres de la découpe intelligente ont été enregistrés.\n"
            f"Attributs uniques: {', '.join(unique_attrs) if unique_attrs else 'Aucun'}"
        )
        
        super(FormSmartCutConfig, self).accept()
