# -*- coding: utf-8 -*-
"""
SmartCutHelper - Utility functions for smart polygon cutting

Helper functions for managing unique attributes configuration and 
polygon split operations.

Created on January 7, 2026
@author: GitHub Copilot
"""

from qgis.core import QgsSettings, QgsField, QgsVectorLayer
from .PluginLogger import PluginLogger


class SmartCutHelper:
    """
    Helper class for Smart Cut tool operations.
    Manages configuration and provides utility methods.
    """
    
    # Settings key for storing unique attributes
    SETTINGS_KEY_UNIQUE_ATTRS = "espaceco/smartcut/unique_attributes"
    
    def __init__(self):
        """Initialize the helper."""
        self.__logger = PluginLogger("SmartCutHelper").getPluginLogger()
    
    @staticmethod
    def getUniqueAttributes():
        """
        Retrieve the list of unique attributes from settings.
        
        :return: List of field names that should be unique
        :rtype: list[str]
        """
        settings = QgsSettings()
        attrs = settings.value(SmartCutHelper.SETTINGS_KEY_UNIQUE_ATTRS, "")
        
        if not attrs:
            # Default unique attributes
            return ["cleaabs", "id"]
        
        # Split comma-separated values
        return [attr.strip() for attr in attrs.split(",") if attr.strip()]
    
    @staticmethod
    def setUniqueAttributes(attributes):
        """
        Save the list of unique attributes to settings.
        
        :param attributes: List of field names
        :type attributes: list[str]
        """
        settings = QgsSettings()
        attrs_str = ",".join(attributes)
        settings.setValue(SmartCutHelper.SETTINGS_KEY_UNIQUE_ATTRS, attrs_str)
        
        logger = PluginLogger("SmartCutHelper").getPluginLogger()
        logger.info(f"Unique attributes saved: {attrs_str}")
    
    @staticmethod
    def getLayerFieldNames(layer):
        """
        Get all field names from a layer.
        
        :param layer: Vector layer
        :type layer: QgsVectorLayer
        :return: List of field names
        :rtype: list[str]
        """
        if not layer or not isinstance(layer, QgsVectorLayer):
            return []
        
        return [field.name() for field in layer.fields()]
    
    @staticmethod
    def calculatePolygonArea(geometry):
        """
        Calculate the area of a polygon geometry.
        
        :param geometry: Polygon geometry
        :type geometry: QgsGeometry
        :return: Area in square meters (or layer units)
        :rtype: float
        """
        if not geometry or geometry.isEmpty():
            return 0.0
        
        return geometry.area()
    
    @staticmethod
    def formatArea(area, precision=2):
        """
        Format area value for display.
        
        :param area: Area value
        :type area: float
        :param precision: Number of decimal places
        :type precision: int
        :return: Formatted string
        :rtype: str
        """
        if area >= 1000000:
            # Convert to km²
            return f"{area / 1000000:.{precision}f} km²"
        elif area >= 10000:
            # Convert to hectares
            return f"{area / 10000:.{precision}f} ha"
        else:
            return f"{area:.{precision}f} m²"
    
    @staticmethod
    def isFieldNumeric(field):
        """
        Check if a field is numeric type.
        
        :param field: Field to check
        :type field: QgsField
        :return: True if numeric
        :rtype: bool
        """
        # QVariant types: 1=Bool, 2=Int, 3=UInt, 4=LongLong, 6=Double
        return field.type() in [1, 2, 3, 4, 6]
    
    @staticmethod
    def getNullValue(field):
        """
        Get appropriate NULL value for a field type.
        
        :param field: Field
        :type field: QgsField
        :return: NULL value (None for numeric, empty string for text)
        """
        if SmartCutHelper.isFieldNumeric(field):
            return None
        else:
            return ""
    
    @staticmethod
    def validateUniqueAttributes(layer, attributes):
        """
        Validate that the specified unique attributes exist in the layer.
        
        :param layer: Vector layer
        :type layer: QgsVectorLayer
        :param attributes: List of attribute names to validate
        :type attributes: list[str]
        :return: Tuple of (valid_attrs, invalid_attrs)
        :rtype: tuple
        """
        if not layer or not isinstance(layer, QgsVectorLayer):
            return ([], attributes)
        
        layer_fields = SmartCutHelper.getLayerFieldNames(layer)
        valid = [attr for attr in attributes if attr in layer_fields]
        invalid = [attr for attr in attributes if attr not in layer_fields]
        
        return (valid, invalid)
    
    @staticmethod
    def getDefaultUniqueAttributesForLayer(layer):
        """
        Get default unique attributes by analyzing layer fields.
        Looks for fields with names suggesting uniqueness (id, cleaabs, etc.)
        
        :param layer: Vector layer
        :type layer: QgsVectorLayer
        :return: List of likely unique field names
        :rtype: list[str]
        """
        if not layer or not isinstance(layer, QgsVectorLayer):
            return []
        
        # Keywords that suggest unique identifiers
        unique_keywords = [
            'id', 'cleaabs', 'uid', 'uuid', 'identifier',
            'code', 'numero', 'num', 'fid', 'objectid'
        ]
        
        potential_unique = []
        for field in layer.fields():
            field_name_lower = field.name().lower()
            # Check if field name contains any unique keyword
            for keyword in unique_keywords:
                if keyword in field_name_lower:
                    potential_unique.append(field.name())
                    break
        
        logger = PluginLogger("SmartCutHelper").getPluginLogger()
        logger.info(f"Auto-detected potential unique attributes: {potential_unique}")
        
        return potential_unique
    
    @staticmethod
    def compareFeaturesArea(features_with_areas):
        """
        Sort features by area (largest first).
        
        :param features_with_areas: List of dicts with 'feature' and 'area' keys
        :type features_with_areas: list[dict]
        :return: Sorted list
        :rtype: list[dict]
        """
        return sorted(
            features_with_areas, 
            key=lambda x: x.get('area', 0), 
            reverse=True
        )
