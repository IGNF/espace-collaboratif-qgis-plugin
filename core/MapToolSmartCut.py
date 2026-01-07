# -*- coding: utf-8 -*-
"""
MapToolSmartCut - Custom cutting tool for polygons and lines that manages unique attributes

This tool allows users to:
- Cut polygons with a line, automatically assigning unique attributes to the larger piece
- Split lines by clicking a separation point, assigning unique attributes to the longer segment

Created on January 7, 2026
@author: GitHub Copilot
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtWidgets import QMessageBox, QApplication
from qgis.core import (
    QgsPointXY, QgsGeometry, QgsFeature, QgsWkbTypes,
    QgsVectorLayer, QgsFeatureRequest, QgsProject
)
from qgis.gui import QgsMapTool, QgsRubberBand, QgsVertexMarker
from .PluginLogger import PluginLogger


class MapToolSmartCut(QgsMapTool):
    """
    Custom map tool for intelligently cutting polygons and lines while managing unique attributes.
    
    This tool extends QgsMapTool to allow users to:
    - Draw a cutting line across a selected polygon
    - Click on a line to place a separation point
    
    After cutting, it calculates areas (polygons) or lengths (lines) and assigns 
    unique attributes only to the larger/longer piece.
    """
    
    # Signal emitted when cut operation is complete
    cutComplete = pyqtSignal(bool, str)
    
    def __init__(self, canvas, context, uniqueAttributes=None):
        """
        Initialize the Smart Cut tool.
        
        :param canvas: QGIS map canvas
        :type canvas: QgsMapCanvas
        :param context: Plugin context containing configuration and state
        :type context: Contexte
        :param uniqueAttributes: List of attribute names that should only belong to larger polygon
        :type uniqueAttributes: list[str]
        """
        # Initialize QgsMapTool base class
        super(MapToolSmartCut, self).__init__(canvas)
        
        self.__logger = PluginLogger("MapToolSmartCut").getPluginLogger()
        self.__context = context
        self.__canvas = canvas
        self.__uniqueAttributes = uniqueAttributes or []
        
        # Visual feedback elements
        self.__rubberBand = None
        self.__tempRubberBand = None
        self.__previewBands = []
        
        # State tracking
        self.__selectedFeature = None
        self.__selectedLayer = None
        self.__cutLine = None
        self.__capturedPoints = []  # Store captured points manually
        
        # Set cursor
        self.setCursor(QCursor(Qt.CrossCursor))
        
        self.__logger.info("MapToolSmartCut initialized")
    
    def setUniqueAttributes(self, attributes):
        """
        Set the list of attributes that should be unique to the larger polygon.
        
        :param attributes: List of field names
        :type attributes: list[str]
        """
        self.__uniqueAttributes = attributes
        self.__logger.info(f"Unique attributes set: {attributes}")
    
    def activate(self):
        """
        Called when the tool is activated.
        Validates selection and prepares for cutting.
        """
        super(MapToolSmartCut, self).activate()
        
        # Check if we have a valid line or polygon layer selected
        layer = self.__canvas.currentLayer()
        if not layer or not isinstance(layer, QgsVectorLayer):
            self.__showError("Veuillez sélectionner une couche vectorielle.")
            self.deactivate()
            return
        
        geom_type = layer.geometryType()
        if geom_type not in [QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry]:
            self.__showError("Cet outil ne fonctionne qu'avec des couches de lignes ou de polygones.")
            self.deactivate()
            return
        
        # Check if layer is in edit mode
        if not layer.isEditable():
            reply = QMessageBox.question(
                None,
                "Mode édition",
                "La couche doit être en mode édition. Activer le mode édition ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                layer.startEditing()
            else:
                self.deactivate()
                return
        
        # Check for selected features
        selectedFeatures = layer.selectedFeatures()
        if len(selectedFeatures) == 0:
            self.__showError("Veuillez sélectionner un polygone à découper.")
            self.deactivate()
            return
        
        if len(selectedFeatures) > 1:
            self.__showError("Veuillez ne sélectionner qu'un seul polygone à la fois.")
            self.deactivate()
            return
        
        self.__selectedFeature = selectedFeatures[0]
        self.__selectedLayer = layer
        
        # Create rubber band for visual feedback
        self.__createRubberBand()
        
        # Show instructions based on geometry type
        if layer.geometryType() == QgsWkbTypes.LineGeometry:
            message = "Cliquez sur la ligne pour placer un point de séparation."
        else:
            message = "Tracez une ligne pour découper le polygone. Clic droit pour terminer."
        
        self.__context.iface.messageBar().pushMessage(
            "Découpe intelligente",
            message,
            level=0,
            duration=5
        )
        
        self.__logger.info("Smart Cut tool activated successfully")
    
    def deactivate(self):
        """
        Called when tool is deactivated. Clean up visual elements.
        """
        self.__clearRubberBands()
        super(MapToolSmartCut, self).deactivate()
        self.__logger.info("Smart Cut tool deactivated")
    
    def __createRubberBand(self):
        """
        Create rubber band for drawing the cut line.
        """
        if self.__rubberBand is None:
            self.__rubberBand = QgsRubberBand(self.__canvas, QgsWkbTypes.LineGeometry)
            self.__rubberBand.setColor(QColor(255, 0, 0, 180))
            self.__rubberBand.setWidth(2)
    
    def __clearRubberBands(self):
        """
        Clear all rubber bands from canvas.
        """
        if self.__rubberBand:
            self.__canvas.scene().removeItem(self.__rubberBand)
            self.__rubberBand = None
        
        for band in self.__previewBands:
            self.__canvas.scene().removeItem(band)
        self.__previewBands.clear()
    
    def canvasMoveEvent(self, event):
        """
        Handle mouse move to show line preview.
        
        :param event: Mouse event
        """
        if len(self.__capturedPoints) > 0 and self.__rubberBand:
            # Update rubber band to show preview of line to current mouse position
            map_pos = self.toMapCoordinates(event.pos())
            self.__rubberBand.reset(QgsWkbTypes.LineGeometry)
            for point in self.__capturedPoints:
                self.__rubberBand.addPoint(point)
            self.__rubberBand.addPoint(map_pos)
    
    def canvasPressEvent(self, event):
        """
        Handle mouse press event.
        
        :param event: Mouse event
        """
        # Left click adds a point
        if event.button() == Qt.LeftButton:
            map_point = self.toMapCoordinates(event.pos())
            self.__capturedPoints.append(map_point)
            
            if self.__rubberBand:
                self.__rubberBand.addPoint(map_point)
            
            # For line geometry, one click is enough to split
            if self.__selectedLayer and self.__selectedLayer.geometryType() == QgsWkbTypes.LineGeometry:
                if len(self.__capturedPoints) == 1:
                    self.__splitLineAtPoint()
            elif len(self.__capturedPoints) == 1:
                self.__context.iface.messageBar().pushMessage(
                    "Découpe intelligente",
                    "Continuez à cliquer pour tracer la ligne. Clic droit pour terminer.",
                    level=0,
                    duration=3
                )
    
    def keyPressEvent(self, event):
        """
        Handle key press events.
        
        :param event: Key event
        """
        # Escape to cancel
        if event.key() == Qt.Key_Escape:
            self.__cancelCut()
        # Enter to finish
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.__finishCut()
        else:
            super(MapToolSmartCut, self).keyPressEvent(event)
    
    def canvasReleaseEvent(self, event):
        """
        Handle canvas release event (right-click to finish).
        
        :param event: Mouse event
        """
        if event.button() == Qt.RightButton:
            self.__finishCut()
    
    def __finishCut(self):
        """
        Complete the cutting operation and process the split.
        """
        # Get the captured points
        if len(self.__capturedPoints) < 2:
            self.__showError("La ligne de coupe doit avoir au moins 2 points.")
            self.__cancelCut()
            return
        
        # Create geometry from captured points
        self.__cutLine = QgsGeometry.fromPolylineXY(self.__capturedPoints)
        
        if self.__cutLine.isEmpty() or not self.__cutLine.isGeosValid():
            self.__showError("La ligne de coupe n'est pas valide.")
            self.__cancelCut()
            return
        
        # Execute the split for polygons
        self.__executeSplitPolygon()
    
    def __splitLineAtPoint(self):
        """
        Split a line at the clicked point.
        """
        if not self.__selectedFeature or not self.__selectedLayer or not self.__capturedPoints:
            self.__showError("Données de découpe invalides.")
            return
        
        try:
            layer = self.__selectedLayer
            feature = self.__selectedFeature
            line_geom = feature.geometry()
            click_point = self.__capturedPoints[0]
            
            # Find the closest point on the line
            closest_point, _, _, _ = line_geom.closestSegmentWithContext(click_point)
            closest_point_geom = QgsGeometry.fromPointXY(closest_point)
            
            # Show visual marker
            marker = QgsVertexMarker(self.__canvas)
            marker.setCenter(closest_point)
            marker.setColor(QColor(255, 0, 0))
            marker.setIconSize(10)
            marker.setIconType(QgsVertexMarker.ICON_X)
            marker.setPenWidth(3)
            
            # Split the line at this point
            split_geoms = []
            line_vertices = line_geom.asPolyline()
            
            # Find the segment where to split
            min_dist = float('inf')
            split_index = 0
            for i in range(len(line_vertices) - 1):
                seg_start = line_vertices[i]
                seg_end = line_vertices[i + 1]
                seg_geom = QgsGeometry.fromPolylineXY([seg_start, seg_end])
                dist = seg_geom.distance(closest_point_geom)
                if dist < min_dist:
                    min_dist = dist
                    split_index = i
            
            # Create two line segments
            if split_index >= 0:
                # First segment: from start to split point
                first_part = line_vertices[:split_index + 1] + [closest_point]
                geom1 = QgsGeometry.fromPolylineXY(first_part)
                
                # Second segment: from split point to end
                second_part = [closest_point] + line_vertices[split_index + 1:]
                geom2 = QgsGeometry.fromPolylineXY(second_part)
                
                split_geoms = [
                    {'geometry': geom1, 'length': geom1.length()},
                    {'geometry': geom2, 'length': geom2.length()}
                ]
            
            if len(split_geoms) < 2:
                self.__showError("Impossible de découper la ligne à cet endroit.")
                marker.hide()
                self.__cancelCut()
                return
            
            # Sort by length (longest first)
            split_geoms.sort(key=lambda x: x['length'], reverse=True)
            
            # Show confirmation
            lengths_text = "\n".join([
                f"Segment {i+1}: {s['length']:.2f} m {'(garde attributs uniques)' if i == 0 else '(perd attributs uniques)'}"
                for i, s in enumerate(split_geoms)
            ])
            
            reply = QMessageBox.question(
                None,
                "Confirmer la découpe",
                f"La découpe créera {len(split_geoms)} segments:\n\n{lengths_text}\n\n"
                f"Les attributs uniques ({', '.join(self.__uniqueAttributes)}) "
                f"seront conservés sur le segment le plus long.\n\nContinuer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            marker.hide()
            
            if reply != QMessageBox.Yes:
                self.__cancelCut()
                return
            
            # Apply the split
            layer.beginEditCommand("Découpe intelligente de ligne")
            
            # Update original feature with first segment
            layer.changeGeometry(feature.id(), split_geoms[0]['geometry'])
            
            # Create new feature for second segment
            newFeature = QgsFeature(layer.fields())
            newFeature.setGeometry(split_geoms[1]['geometry'])
            
            # Copy attributes
            for field in layer.fields():
                fieldName = field.name()
                originalValue = feature.attribute(fieldName)
                
                # Clear unique attributes on shorter segment
                if fieldName in self.__uniqueAttributes:
                    if field.type() in [1, 2, 3, 4, 6]:  # Integer types
                        newFeature.setAttribute(fieldName, None)
                    else:
                        newFeature.setAttribute(fieldName, '')
                    self.__logger.info(f"Cleared unique attribute '{fieldName}' on shorter segment")
                else:
                    newFeature.setAttribute(fieldName, originalValue)
            
            layer.addFeature(newFeature)
            layer.endEditCommand()
            
            # Refresh
            layer.triggerRepaint()
            self.__canvas.refresh()
            
            # Success message
            self.__context.iface.messageBar().pushMessage(
                "Succès",
                f"Ligne découpée en {len(split_geoms)} segments. "
                f"Attributs uniques conservés sur le segment le plus long.",
                level=3,
                duration=5
            )
            
            self.cutComplete.emit(True, f"Split line into {len(split_geoms)} segments")
            self.__logger.info("Smart line cut completed successfully")
            
            # Clean up
            self.__cleanup()
            
        except Exception as e:
            self.__logger.error(f"Error during line split: {str(e)}")
            if self.__selectedLayer:
                self.__selectedLayer.destroyEditCommand()
            self.__showError(f"Erreur lors de la découpe: {str(e)}")
            self.cutComplete.emit(False, str(e))
    
    def __executeSplitPolygon(self):
        """
        Execute the polygon split and manage attributes.
        """
        if not self.__selectedFeature or not self.__selectedLayer or not self.__cutLine:
            self.__showError("Données de découpe invalides.")
            return
        
        try:
            layer = self.__selectedLayer
            feature = self.__selectedFeature
            originalGeom = feature.geometry()
            
            # Split the geometry
            # Convert QgsPoint to QgsPointXY for splitGeometry
            cutLinePoints = [QgsPointXY(pt) for pt in self.__cutLine.asPolyline()]
            result, newGeometries, topologyTestPoints = originalGeom.splitGeometry(
                cutLinePoints, 
                False  # topological editing
            )
            
            if result != 0:
                self.__showError(f"Erreur lors de la découpe: code {result}")
                self.__cancelCut()
                return
            
            # Calculate areas of all resulting polygons
            polygons = []
            
            # Modified original geometry
            if not originalGeom.isEmpty():
                polygons.append({
                    'geometry': QgsGeometry(originalGeom),
                    'area': originalGeom.area(),
                    'is_original': True,
                    'fid': feature.id()
                })
            
            # New geometries created by split
            for geom in newGeometries:
                if not geom.isEmpty():
                    polygons.append({
                        'geometry': QgsGeometry(geom),
                        'area': geom.area(),
                        'is_original': False,
                        'fid': None
                    })
            
            if len(polygons) < 2:
                self.__showError("La découpe n'a pas créé de nouveaux polygones.")
                self.__cancelCut()
                return
            
            # Sort by area (largest first)
            polygons.sort(key=lambda x: x['area'], reverse=True)
            largest = polygons[0]
            
            self.__logger.info(f"Split created {len(polygons)} polygons. Largest area: {largest['area']:.2f}")
            
            # Show confirmation dialog with area information
            areas_text = "\n".join([
                f"Polygone {i+1}: {p['area']:.2f} m² {'(garde attributs uniques)' if i == 0 else '(perd attributs uniques)'}"
                for i, p in enumerate(polygons)
            ])
            
            reply = QMessageBox.question(
                None,
                "Confirmer la découpe",
                f"La découpe créera {len(polygons)} polygones:\n\n{areas_text}\n\n"
                f"Les attributs uniques ({', '.join(self.__uniqueAttributes)}) "
                f"seront conservés sur le plus grand polygone.\n\nContinuer ?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                self.__cancelCut()
                return
            
            # Apply the split
            layer.beginEditCommand("Découpe intelligente")
            
            # Update the original feature with modified geometry
            layer.changeGeometry(feature.id(), polygons[0]['geometry'])
            
            # Create new features for the additional polygons
            for i, poly_info in enumerate(polygons[1:], start=1):
                newFeature = QgsFeature(layer.fields())
                newFeature.setGeometry(poly_info['geometry'])
                
                # Copy all attributes from original
                for field in layer.fields():
                    fieldName = field.name()
                    originalValue = feature.attribute(fieldName)
                    
                    # Clear unique attributes on smaller polygons
                    if fieldName in self.__uniqueAttributes:
                        # Set to NULL or empty
                        if field.type() in [1, 2, 3, 4, 6]:  # Integer types
                            newFeature.setAttribute(fieldName, None)
                        else:
                            newFeature.setAttribute(fieldName, '')
                        self.__logger.info(f"Cleared unique attribute '{fieldName}' on smaller polygon {i}")
                    else:
                        newFeature.setAttribute(fieldName, originalValue)
                
                layer.addFeature(newFeature)
            
            layer.endEditCommand()
            
            # Refresh canvas
            layer.triggerRepaint()
            self.__canvas.refresh()
            
            # Success message
            self.__context.iface.messageBar().pushMessage(
                "Succès",
                f"Polygone découpé en {len(polygons)} morceaux. "
                f"Attributs uniques conservés sur le plus grand polygone.",
                level=3,
                duration=5
            )
            
            self.cutComplete.emit(True, f"Split into {len(polygons)} polygons")
            self.__logger.info("Smart cut completed successfully")
            
            # Clean up and deactivate
            self.__cleanup()
            
        except Exception as e:
            self.__logger.error(f"Error during smart cut: {str(e)}")
            if self.__selectedLayer:
                self.__selectedLayer.destroyEditCommand()
            self.__showError(f"Erreur lors de la découpe: {str(e)}")
            self.cutComplete.emit(False, str(e))
    
    def __cancelCut(self):
        """
        Cancel the current cut operation.
        """
        self.__capturedPoints.clear()
        self.__clearRubberBands()
        self.__logger.info("Cut operation cancelled")
    
    def __cleanup(self):
        """
        Clean up after successful cut.
        """
        self.__capturedPoints.clear()
        self.__clearRubberBands()
        self.__selectedFeature = None
        self.__selectedLayer = None
        self.__cutLine = None
    
    def __showError(self, message):
        """
        Display error message to user.
        
        :param message: Error message
        :type message: str
        """
        self.__logger.warning(message)
        self.__context.iface.messageBar().pushMessage(
            "Erreur",
            message,
            level=2,
            duration=5
        )
