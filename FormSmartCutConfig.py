# -*- coding: utf-8 -*-
"""
FormSmartCutConfig - Configuration dialog for Smart Cut tool

Dialog to configure which attributes should remain unique when cutting polygons.

Created on January 7, 2026
@author: GitHub Copilot
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QLineEdit, QMessageBox, QGroupBox, QListWidgetItem,
    QAbstractItemView
)
from PyQt5.QtCore import Qt
from qgis.core import QgsVectorLayer, QgsWkbTypes
from .core.SmartCutHelper import SmartCutHelper
from .core.PluginLogger import PluginLogger


class FormSmartCutConfig(QDialog):
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
        
        self.__context = context
        self.__logger = PluginLogger("FormSmartCutConfig").getPluginLogger()
        
        self.setWindowTitle("Configuration - Découpe intelligente")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.__setupUI()
        self.__loadSettings()
    
    def __setupUI(self):
        """
        Set up the user interface.
        """
        layout = QVBoxLayout()
        
        # Title and description
        title = QLabel("<h3>Configuration de la découpe intelligente</h3>")
        layout.addWidget(title)
        
        description = QLabel(
            "Sélectionnez les attributs qui doivent rester uniques.\n"
            "Lors d'une découpe, ces attributs ne seront conservés que sur le plus grand polygone."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Available fields from current layer
        layer_group = QGroupBox("Attributs de la couche active")
        layer_layout = QVBoxLayout()
        
        layer_info = QLabel("Couche: <i>Aucune couche sélectionnée</i>")
        layer_info.setObjectName("layerInfo")
        layer_layout.addWidget(layer_info)
        
        self.__availableFieldsList = QListWidget()
        self.__availableFieldsList.setSelectionMode(QAbstractItemView.MultiSelection)
        layer_layout.addWidget(self.__availableFieldsList)
        
        refresh_btn = QPushButton("⟳ Actualiser depuis la couche active")
        refresh_btn.clicked.connect(self.__loadFromActiveLayer)
        layer_layout.addWidget(refresh_btn)
        
        layer_group.setLayout(layer_layout)
        layout.addWidget(layer_group)
        
        # Selected unique attributes
        unique_group = QGroupBox("Attributs uniques configurés")
        unique_layout = QVBoxLayout()
        
        unique_label = QLabel(
            "Ces attributs seront conservés uniquement sur le plus grand polygone:"
        )
        unique_label.setWordWrap(True)
        unique_layout.addWidget(unique_label)
        
        self.__uniqueAttrsList = QListWidget()
        self.__uniqueAttrsList.setSelectionMode(QAbstractItemView.MultiSelection)
        unique_layout.addWidget(self.__uniqueAttrsList)
        
        # Buttons to add/remove
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("⬇ Ajouter sélection")
        add_btn.clicked.connect(self.__addSelectedFields)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("⬆ Retirer sélection")
        remove_btn.clicked.connect(self.__removeSelectedFields)
        btn_layout.addWidget(remove_btn)
        
        unique_layout.addLayout(btn_layout)
        
        # Manual entry
        manual_layout = QHBoxLayout()
        manual_label = QLabel("Ajouter manuellement:")
        self.__manualEntry = QLineEdit()
        self.__manualEntry.setPlaceholderText("nom_attribut")
        manual_add_btn = QPushButton("Ajouter")
        manual_add_btn.clicked.connect(self.__addManualField)
        
        manual_layout.addWidget(manual_label)
        manual_layout.addWidget(self.__manualEntry)
        manual_layout.addWidget(manual_add_btn)
        unique_layout.addLayout(manual_layout)
        
        unique_group.setLayout(unique_layout)
        layout.addWidget(unique_group)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        auto_detect_btn = QPushButton("🔍 Détecter automatiquement")
        auto_detect_btn.clicked.connect(self.__autoDetect)
        button_layout.addWidget(auto_detect_btn)
        
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load fields from active layer on startup
        self.__loadFromActiveLayer()
    
    def __loadSettings(self):
        """
        Load unique attributes from settings.
        """
        unique_attrs = SmartCutHelper.getUniqueAttributes()
        
        self.__uniqueAttrsList.clear()
        for attr in unique_attrs:
            self.__uniqueAttrsList.addItem(attr)
        
        self.__logger.info(f"Loaded {len(unique_attrs)} unique attributes from settings")
    
    def __loadFromActiveLayer(self):
        """
        Load field names from the active layer.
        """
        self.__availableFieldsList.clear()
        
        layer = self.__context.iface.activeLayer()
        
        # Update layer info label
        layer_info = self.findChild(QLabel, "layerInfo")
        
        if not layer or not isinstance(layer, QgsVectorLayer):
            if layer_info:
                layer_info.setText("Couche: <i>Aucune couche vectorielle active</i>")
            return
        
        if layer.geometryType() != QgsWkbTypes.PolygonGeometry:
            if layer_info:
                layer_info.setText(f"Couche: <b>{layer.name()}</b> <i>(pas une couche de polygones)</i>")
            return
        
        if layer_info:
            layer_info.setText(f"Couche: <b>{layer.name()}</b>")
        
        # Load fields
        field_names = SmartCutHelper.getLayerFieldNames(layer)
        for field_name in field_names:
            self.__availableFieldsList.addItem(field_name)
        
        self.__logger.info(f"Loaded {len(field_names)} fields from layer '{layer.name()}'")
    
    def __addSelectedFields(self):
        """
        Add selected fields from available list to unique attributes list.
        """
        selected_items = self.__availableFieldsList.selectedItems()
        
        if not selected_items:
            return
        
        # Get current unique attributes
        current_attrs = [
            self.__uniqueAttrsList.item(i).text()
            for i in range(self.__uniqueAttrsList.count())
        ]
        
        # Add new ones
        for item in selected_items:
            field_name = item.text()
            if field_name not in current_attrs:
                self.__uniqueAttrsList.addItem(field_name)
                self.__logger.info(f"Added unique attribute: {field_name}")
    
    def __removeSelectedFields(self):
        """
        Remove selected fields from unique attributes list.
        """
        selected_items = self.__uniqueAttrsList.selectedItems()
        
        for item in selected_items:
            row = self.__uniqueAttrsList.row(item)
            self.__uniqueAttrsList.takeItem(row)
            self.__logger.info(f"Removed unique attribute: {item.text()}")
    
    def __addManualField(self):
        """
        Add manually entered field name to unique attributes.
        """
        field_name = self.__manualEntry.text().strip()
        
        if not field_name:
            return
        
        # Check if already exists
        for i in range(self.__uniqueAttrsList.count()):
            if self.__uniqueAttrsList.item(i).text() == field_name:
                QMessageBox.warning(
                    self,
                    "Attribut existant",
                    f"L'attribut '{field_name}' est déjà dans la liste."
                )
                return
        
        self.__uniqueAttrsList.addItem(field_name)
        self.__manualEntry.clear()
        self.__logger.info(f"Manually added unique attribute: {field_name}")
    
    def __autoDetect(self):
        """
        Auto-detect unique attributes from the active layer.
        """
        layer = self.__context.iface.activeLayer()
        
        if not layer or not isinstance(layer, QgsVectorLayer):
            QMessageBox.warning(
                self,
                "Aucune couche",
                "Veuillez sélectionner une couche vectorielle."
            )
            return
        
        detected = SmartCutHelper.getDefaultUniqueAttributesForLayer(layer)
        
        if not detected:
            QMessageBox.information(
                self,
                "Aucun attribut détecté",
                "Aucun attribut unique n'a été détecté automatiquement.\n"
                "Veuillez les sélectionner manuellement."
            )
            return
        
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Attributs détectés",
            f"Les attributs suivants ont été détectés:\n\n" +
            "\n".join(f"• {attr}" for attr in detected) +
            "\n\nRemplacer la configuration actuelle ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.__uniqueAttrsList.clear()
            for attr in detected:
                self.__uniqueAttrsList.addItem(attr)
            self.__logger.info(f"Auto-detected and set {len(detected)} unique attributes")
    
    def accept(self):
        """
        Save settings and close dialog.
        """
        # Get all unique attributes
        unique_attrs = [
            self.__uniqueAttrsList.item(i).text()
            for i in range(self.__uniqueAttrsList.count())
        ]
        
        if not unique_attrs:
            reply = QMessageBox.question(
                self,
                "Aucun attribut",
                "Aucun attribut unique n'est configuré.\n"
                "Voulez-vous vraiment continuer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Save to settings
        SmartCutHelper.setUniqueAttributes(unique_attrs)
        
        QMessageBox.information(
            self,
            "Configuration enregistrée",
            f"Configuration enregistrée avec {len(unique_attrs)} attribut(s) unique(s)."
        )
        
        self.__logger.info(f"Saved {len(unique_attrs)} unique attributes to settings")
        
        super(FormSmartCutConfig, self).accept()
