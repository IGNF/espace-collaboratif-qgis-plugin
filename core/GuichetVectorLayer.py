# -*- coding: utf-8 -*-
"""
Created on 23 oct. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""
import random

from PyQt5.QtGui import QColor
from qgis.core import QgsVectorLayer, QgsProject, QgsEditorWidgetSetup, QgsSymbol, QgsFeatureRenderer, \
    QgsRuleBasedRenderer, QgsSingleSymbolRenderer, QgsLineSymbol, QgsFillSymbol, QgsMarkerSymbol, QgsUnitTypes, \
    QgsDefaultValue

from .MongoDBtoQGIS import MongoDBtoQGIS


class GuichetVectorLayer(QgsVectorLayer):
    databasename = None
    correspondanceChampType = None
    sqliteManager = None
    srid = None
    # Juste pour savoir si cette couche est de type 'standard' ou 'bduni' avec gcms_fingerprint
    isStandard = None
    idNameForDatabase = None
    geometryNameForDatabase = None
    geometryDimensionForDatabase = None
    geometryTypeForDatabase = None

    def __init__(self, parameters):
        super(GuichetVectorLayer, self).__init__(parameters['uri'], parameters['name'], parameters['genre'])
        self.databasename = parameters['databasename']
        self.sqliteManager = parameters['sqliteManager']
        self.srid = -1
        self.isStandard = True
        self.idNameForDatabase = parameters['idName']
        self.geometryNameForDatabase = parameters['geometryName']
        self.geometryDimensionForDatabase = parameters['geometryDimension']
        self.geometryTypeForDatabase = parameters['geometryType']
        self.connectSignals()

    '''
    Connexion des signaux pour les évènements survenus sur la carte
    '''
    def connectSignals(self):
        self.editingStopped.connect(self.editing_stopped)
        self.beforeRollBack.connect(self.before_rollback)

    '''
    L'utilisateur a mis fin à l'édition de la couche
    '''
    def editing_stopped(self):
        print("Fin édition de la couche")

    '''
    L'utilisateur a annulé toutes ses modifications
    '''
    def before_rollback(self):
        print("Annulation des modifications dans la couche")

    '''
        Transformation de la condition en expression QGIS
        La condition '{"$and" : [{"zone" : "Zone1"}]}' doit devenir '"zone" LIKE \"Zone1\"'
        et doit se traduire dans QGIS par "zone" LIKE 'Zone1'
        TODO : manque le traitement du AND, OR, etc...
    '''
    def changeConditionToExpression(self, condition, bExpression):
        # Pas de style pour la couche, style QGIS par défaut
        if bExpression is False and condition is None or condition == '':
            return ''

        # Pas de rule style, capture de toutes les autres entités
        if bExpression is True and condition is None:
            return "ELSE"

        mongo = MongoDBtoQGIS(condition, self.correspondanceChampType)
        return mongo.run()

    '''
        Récupère la couleur en fonction du type de géométrie
    '''
    def getColorFromType(self, data):

        if data['type'] == 'line':
            return data['strokeColor']

        if data['type'] == 'polygon':
            return data['fillColor']

        # La symbologie d'un point dans l'espace collaboratif est un symbole.
        # Pour l'instant, un point se voit attribuer une couleur aléatoire
        if data['type'] == 'point':
            # il faudrait retourner data['externalGraphic']
            # et puis peut-être
            # "graphicWidth": 25,
            # "graphicHeight": 25,
            # "graphicOpacity": 1,']
            # random color
            random_color_point = f"#{random.randrange(0x1000000):06x}"
            return random_color_point

        return ""

    '''
        Récupère l'opacité de la couche
    '''
    def getOpacity(self, data):

        if data['type'] == 'line':
            return data['strokeOpacity']

        if data['type'] == 'polygon':
            return data['fillOpacity']

        if data['type'] == 'point':
            # fully opaque
            return 1

        return 1

    '''
        Récupère la taille du symbole
    '''
    def getWidth(self, data):

        if data['type'] == 'line':
            return str(data['strokeWidth'])

        if data['type'] == 'point':
            return 10

        return ''

    def setSymbolLine(self, strokeLinecap, strokeDashstyle, strokeColor, strokeWidth, strokeOpacity):
        lineSymbol = {'capstyle': strokeLinecap, 'line_style': strokeDashstyle,
                      'line_color': strokeColor, 'line_width': strokeWidth,
                      'line_width_unit': 'Pixel'}
        symbol = QgsLineSymbol().createSimple(lineSymbol)
        symbol.setOpacity(strokeOpacity)
        return symbol

    def setSymbolPoint(self, fillColor, strokeColor):
        pointSymbol = {'angle': '0', 'color': fillColor, 'horizontal_anchor_point': '1',
                       'joinstyle': 'round', 'name': 'circle', 'offset': '0,0',
                       'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                       'outline_color': strokeColor, 'outline_style': 'solid',
                       'outline_width': '2', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0',
                       'outline_width_unit': 'Pixel', 'scale_method': 'diameter', 'size': '10',
                       'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'Pixel',
                       'vertical_anchor_point': '1'}
        symbol = QgsMarkerSymbol().createSimple(pointSymbol)
        symbol.setOpacity(1)
        return symbol

    def setSymbolPolygon(self, fillColor, strokeColor, strokeDashstyle, strokeWidth, fillOpacity):
        polygonSymbol = {'color': fillColor, 'outline_color': strokeColor,
                         'outline_style': strokeDashstyle, 'outline_width': strokeWidth,
                         'outline_width_unit': 'Pixel'}
        symbol = QgsFillSymbol().createSimple(polygonSymbol)
        symbol.setOpacity(fillOpacity)
        return symbol

    '''
        Symbologie extraite du style Collaboratif par défaut
    '''
    def setModifyWithQgsSingleDefaultSymbolRenderer(self):
        geomType = self.geometryType()
        symbol = None

        # 'Point'
        if geomType == 0:
            pointSymbol = {'angle': '0', 'color': '238,153,0,255', 'horizontal_anchor_point': '1', 'joinstyle': 'round',
                           'name': 'circle', 'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0',
                           'offset_unit': 'Pixel', 'outline_color': '238,153,0,255', 'outline_style': 'solid',
                           'outline_width': '2', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0',
                           'outline_width_unit': 'Pixel', 'scale_method': 'diameter', 'size': '10',
                           'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'Pixel', 'vertical_anchor_point': '1'}
            symbol = QgsMarkerSymbol().createSimple(pointSymbol)
            symbol.setOpacity(0.5)

        # 'Polygon'
        if geomType == 2:
            polygonSymbol = {'border_width_map_unit_scale': '3x:0,0,0,0,0,0', 'color': '238,153,0,255',
                             'joinstyle': 'miter', 'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0',
                             'offset_unit': 'Pixel', 'outline_color': '255,255,255,0', 'outline_style': 'no',
                             'outline_width': '0', 'outline_width_unit': 'Pixel', 'style': 'solid'}
            symbol = QgsFillSymbol().createSimple(polygonSymbol)
            symbol.setOpacity(0.5)

        # 'LineString'
        if geomType == 1:
            lineSymbol = {'capstyle': 'square', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                          'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'bevel',
                          'line_color': '238,153,0,255', 'line_style': 'solid', 'line_width': '2',
                          'line_width_unit': 'Pixel', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0',
                          'offset_unit': 'Pixel', 'ring_filter': '0', 'use_custom_dash': '0',
                          'width_map_unit_scale': '3x:0,0,0,0,0,0'}
            symbol = QgsLineSymbol().createSimple(lineSymbol)
            symbol.setOpacity(1)

        if symbol is None:
            symbol = QgsSymbol.defaultSymbol(geomType)
            symbol.setColor(QColor('238,153,0,255'))
            symbol.setOpacity(1)

        symbol.setOutputUnit(QgsUnitTypes.RenderPixels)
        renderer = QgsSingleSymbolRenderer(symbol)
        # apply the renderer to the layer
        self.setRenderer(renderer)
        # Refresh layer
        self.triggerRepaint()

    def setModifyWithQgsSingleSymbolRenderer(self, data):
        symbol = None
        for c, v in data.items():

            if v['type'] == 'line':
                symbol = self.setSymbolLine(v["strokeLinecap"], v["strokeDashstyle"], v["strokeColor"],
                                            str(v["strokeWidth"]), v['strokeOpacity'])

            if v['type'] == 'polygon':
                symbol = self.setSymbolPolygon(v["fillColor"], v['strokeColor'], v['strokeDashstyle'],
                                               str(v['strokeWidth']),
                                               v['fillOpacity'])

            if v['type'] == 'point':
                fillcolor = v["fillColor"]
                if fillcolor is None:
                    fillcolor = QColor(f"#{random.randrange(0x1000000):06x}")

                strokecolor = v['strokeColor']
                if strokecolor is None:
                    strokecolor = QColor(f"#{random.randrange(0x1000000):06x}")

                symbol = self.setSymbolPoint(fillcolor, strokecolor)

        if symbol is None:
            symbol = QgsSymbol.defaultSymbol(self.geometryType())
            symbol.setColor(QColor('238,153,0,255'))
            symbol.setOpacity(1)

        symbol.setOutputUnit(QgsUnitTypes.RenderPixels)
        renderer = QgsSingleSymbolRenderer(symbol)
        # apply the renderer to the layer
        self.setRenderer(renderer)
        # Refresh layer
        self.triggerRepaint()

    def setModifyWithQgsRuleBasedSymbolRenderer(self, data, bExpression):
        # class_rules = ('label=name', 'expression=condition', 'color=fillColor/strokeColor',
        # 'opacity=fillOpacity/strokeOpacity' )
        class_rules = []
        for c, v in data.items():
            tmp = [v['name']]
            expression = self.changeConditionToExpression(v['condition'], bExpression)
            tmp.append(expression)
            col = self.getColorFromType(v)
            tmp.append(col)
            opac = self.getOpacity(v)
            tmp.append(opac)
            width = self.getWidth(v)
            tmp.append(width)
            class_rules.append(tmp)

        # create a new rule-based renderer
        symbol = QgsSymbol.defaultSymbol(self.geometryType())
        renderer = QgsRuleBasedRenderer(symbol)

        # get the "root" rule
        root_rule = renderer.rootRule()

        for label, expression, color, opacity, width in class_rules:
            # create a clone (i.e. a copy) of the default rule
            rule = root_rule.children()[0].clone()
            # set the label, opacity, expression and color
            rule.setLabel(label)
            rule.setFilterExpression(expression)
            rule.symbol().setColor(QColor(color))
            rule.symbol().setOpacity(opacity)
            rule.symbol().setOutputUnit(QgsUnitTypes.RenderPixels)
            if width != '':
                if type(width) is str:
                    rule.symbol().setWidth(int(width))
                else:
                    rule.symbol().setSize(width)
            # append the rule to the list of rules
            root_rule.appendChild(rule)

        # delete the default rule
        root_rule.removeChildAt(0)

        # apply the renderer to the layer
        self.setRenderer(renderer)
        # Refresh layer
        self.triggerRepaint()

    '''
        Modification de la symbologie
    '''
    def setModifySymbols(self, listOfValues):

        # Pas de balise Style, Symbologie = Symbole QGIS par défaut
        if len(listOfValues) == 0:
            self.setModifyWithQgsSingleDefaultSymbolRenderer()

        # Une balise Style, Symbologie = Symbole unique
        if len(listOfValues) == 1:
            self.setModifyWithQgsSingleSymbolRenderer(listOfValues)

        # Balise Style avec balise(s) Children, Symbologie = Ensemble de règles
        if len(listOfValues) > 1:
            self.setModifyWithQgsRuleBasedSymbolRenderer(listOfValues, True)

    '''
        Définition de l'échelle minimum et maximum de la couche
        Source : https://geoservices.ign.fr/documentation/geoservices/wmts.html#taille-des-tuiles-en-pixels
    '''
    def setDisplayScale(self, minS, maxS):
        # Correspondance zoom des tuiles - échelle approximative
        scale = {
            '0': 559082264,
            '1': 279541132,
            '2': 139770566,
            '3': 69885283,
            '4': 34942642,
            '5': 17471321,
            '6': 8735660,
            '7': 4367830,
            '8': 2183915,
            '9': 1091958,
            '10': 545979,
            '11': 272989,
            '12': 136495,
            '13': 68247,
            '14': 34124,
            '15': 17062,
            '16': 8531,
            '17': 4265,
            '18': 2133,
            '19': 1066,
            '20': 533,
            '21': 267
        }
        self.setMinimumScale(scale[minS])
        self.setMaximumScale(scale[maxS])
        self.setScaleBasedVisibility(True)
