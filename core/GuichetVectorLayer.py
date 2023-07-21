# -*- coding: utf-8 -*-
"""
Created on 23 oct. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""
import random
import json
from PyQt5.QtGui import QColor
from qgis.core import QgsVectorLayer, QgsSymbol, QgsRuleBasedRenderer, QgsSingleSymbolRenderer, QgsLineSymbol, \
    QgsFillSymbol, QgsMarkerSymbol, QgsUnitTypes, QgsMarkerLineSymbolLayer, QgsSimpleLineSymbolLayer, \
    QgsFontMarkerSymbolLayer, QgsSymbolLayer, QgsProperty

from .MongoDBtoQGIS.ConditionFactory import ConditionFactory


class GuichetVectorLayer(QgsVectorLayer):

    def __init__(self, parameters):
        super(GuichetVectorLayer, self).__init__(parameters['uri'], parameters['name'], parameters['genre'])
        self.databasename = parameters['databasename']
        self.sqliteManager = parameters['sqliteManager']
        self.srid = -1
        self.isBduni = False
        self.idNameForDatabase = parameters['idName']
        self.geometryNameForDatabase = parameters['geometryName']
        self.geometryDimensionForDatabase = parameters['geometryDimension']
        self.geometryTypeForDatabase = parameters['geometryType']
        self.conditionFactory = ConditionFactory()
        self.correspondanceChampType = None

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
        expression = self.conditionFactory.create_condition(condition)
        return expression.toSQL()

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

    def setPointStyle(self, fillColor, strokeColor):
        return {'angle': '0', 'color': fillColor, 'horizontal_anchor_point': '1',
                'joinstyle': 'round', 'name': 'circle', 'offset': '0,0',
                'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                'outline_color': strokeColor, 'outline_style': 'solid',
                'outline_width': '2', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0',
                'outline_width_unit': 'Pixel', 'scale_method': 'diameter', 'size': '10',
                'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'Pixel',
                'vertical_anchor_point': '1'}

    def setLineStyle(self, strokeLinecap, strokeDashstyle, strokeColor, strokeWidth):
        # {'align_dash_pattern': '0', 'capstyle': 'square', 'customdash': '5;2',
        #  'customdash_map_unit_scale': '3x:0,0,0,0,0,0', 'customdash_unit': 'Pixel', 'dash_pattern_offset': '0',
        #  'dash_pattern_offset_map_unit_scale': '3x:0,0,0,0,0,0', 'dash_pattern_offset_unit': 'MM',
        #  'draw_inside_polygon': '0', 'joinstyle': 'round', 'line_color': '128,128,128,255', 'line_style': 'solid',
        #  'line_width': '2', 'line_width_unit': 'Pixel', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0',
        #  'offset_unit': 'Pixel', 'ring_filter': '0', 'trim_distance_end': '0',
        #  'trim_distance_end_map_unit_scale': '3x:0,0,0,0,0,0', 'trim_distance_end_unit': 'MM',
        #  'trim_distance_start': '0', 'trim_distance_start_map_unit_scale': '3x:0,0,0,0,0,0',
        #  'trim_distance_start_unit': 'MM', 'tweak_dash_pattern_on_corners': '0', 'use_custom_dash': '0',
        #  'width_map_unit_scale': '3x:0,0,0,0,0,0'}
        # Correspondance entre un style de l'espace collaboratif et le style QGis
        lineStyles = {
            # Ligne continu -> trait continu
            'solid': {'capstyle': 'solid', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                      'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                      'line_color': strokeColor, 'line_style': 'solid', 'line_width': strokeWidth,
                      'line_width_unit': 'Pixel',
                      'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                      'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne en tiret -> traits courts
            'dash': {'capstyle': 'dash', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                     'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                     'line_color': strokeColor, 'line_style': 'dash', 'line_width': strokeWidth,
                     'line_width_unit': 'Pixel',
                     'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                     'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne en pointillé -> points
            'dot': {'capstyle': 'dot', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                    'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                    'line_color': strokeColor, 'line_style': 'dot', 'line_width': strokeWidth,
                    'line_width_unit': 'Pixel',
                    'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                    'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne tiret-point -> points/traits courts
            'dashdot': {'capstyle': 'dash dot', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                        'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                        'line_color': strokeColor, 'line_style': 'dash dot', 'line_width': strokeWidth,
                        'line_width_unit': 'Pixel', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0',
                        'offset_unit': 'Pixel', 'ring_filter': '0', 'use_custom_dash': '0',
                        'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne tiret-point-point -> points/traits longs
            'longdashdot': {'capstyle': 'dash dot dot', 'customdash': '10;5',
                            'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                            'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                            'line_color': strokeColor, 'line_style': 'dash dot dot', 'line_width': strokeWidth,
                            'line_width_unit': 'Pixel', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0',
                            'offset_unit': 'Pixel', 'ring_filter': '0', 'use_custom_dash': '0',
                            'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne en tiret -> traits longs
            'longdash': {'capstyle': 'dash', 'customdash': '10;5', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                         'customdash_unit': 'Point', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                         'line_color': strokeColor, 'line_style': 'no', 'line_width': strokeWidth,
                         'line_width_unit': 'Pixel',
                         'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                         'ring_filter': '0', 'use_custom_dash': '1', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}
        }
        return lineStyles[strokeDashstyle]

    def setPolygonStyle(self, fillColor, strokeColor, strokeDashstyle, strokeWidth):
        polygonStyles = {
            'solid': {'border_width_map_unit_scale': '3x:0,0,0,0,0,0', 'color': fillColor, 'joinstyle': 'miter',
                      'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                      'outline_color': strokeColor, 'outline_style': 'solid', 'outline_width': strokeWidth,
                      'outline_width_unit': 'Pixel', 'style': 'solid'},
            'dash': {'border_width_map_unit_scale': '3x:0,0,0,0,0,0', 'color': fillColor, 'joinstyle': 'miter',
                     'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                     'outline_color': strokeColor, 'outline_style': 'dash', 'outline_width': strokeWidth,
                     'outline_width_unit': 'Pixel', 'style': 'solid'},
            'dot': {'border_width_map_unit_scale': '3x:0,0,0,0,0,0', 'color': fillColor, 'joinstyle': 'miter',
                    'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                    'outline_color': strokeColor, 'outline_style': 'dot', 'outline_width': strokeWidth,
                    'outline_width_unit': 'Pixel', 'style': 'solid'},
            'dashdot': {'border_width_map_unit_scale': '3x:0,0,0,0,0,0', 'color': '238,153,0,255', 'joinstyle': 'miter',
                        'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                        'outline_color': '0,0,0,255', 'outline_style': 'dash dot', 'outline_width': '0',
                        'outline_width_unit': 'Pixel', 'style': 'solid'},
            'longdashdot': {'border_width_map_unit_scale': '3x:0,0,0,0,0,0', 'color': '238,153,0,255',
                            'joinstyle': 'miter',
                            'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                            'outline_color': '0,0,0,255', 'outline_style': 'dash dot dot', 'outline_width': '0',
                            'outline_width_unit': 'Pixel', 'style': 'solid'},
            'longdash': {'border_width_map_unit_scale': '3x:0,0,0,0,0,0', 'color': fillColor, 'joinstyle': 'miter',
                         'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                         'outline_color': strokeColor, 'outline_style': 'dash', 'outline_width': strokeWidth,
                         'outline_width_unit': 'Pixel', 'style': 'solid'}
        }
        return polygonStyles[strokeDashstyle]

    def setSymbolPoint(self, fillColor, strokeColor, opacity):
        if fillColor is None:
            fillColor = QColor(f"#{random.randrange(0x1000000):06x}").name(QColor.HexRgb)
        if strokeColor is None:
            strokeColor = QColor(f"#{random.randrange(0x1000000):06x}").name(QColor.HexRgb)
        pointSymbol = self.setPointStyle(fillColor, strokeColor)
        symbol = QgsMarkerSymbol().createSimple(pointSymbol)
        symbol.setOpacity(opacity)
        return symbol

    def setSymbolLine(self, strokeLinecap, strokeDashstyle, strokeColor, strokeWidth, strokeOpacity):
        lineSymbol = self.setLineStyle(strokeLinecap, strokeDashstyle, strokeColor, strokeWidth)
        symbol = QgsLineSymbol().createSimple(lineSymbol)
        symbol.setOpacity(strokeOpacity)
        return symbol

    def setSymbolPolygon(self, fillColor, strokeColor, strokeDashstyle, strokeWidth, fillOpacity):
        polygonSymbol = self.setPolygonStyle(fillColor, strokeColor, strokeDashstyle, strokeWidth)
        symbol = QgsFillSymbol().createSimple(polygonSymbol)
        symbol.setOpacity(fillOpacity)
        return symbol

    def setSimpleLineSymbolLayer(self):
        return {'average_angle_length': '4', 'average_angle_map_unit_scale': '3x:0,0,0,0,0,0',
                'average_angle_unit': 'MM',
                'interval': '3', 'interval_map_unit_scale': '3x:0,0,0,0,0,0', 'interval_unit': 'MM', 'offset': '0',
                'offset_along_line': '0', 'offset_along_line_map_unit_scale': '3x:0,0,0,0,0,0',
                'offset_along_line_unit': 'MM',
                'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'placement': 'centralpoint',
                'ring_filter': '0',
                'rotate': '1'}

    def setMarkerLineSymbolLayer(self):
        return {'angle': '0', 'chr': '>', 'color': '0,0,0,255', 'font': 'Arial', 'font_style': 'Normal',
                'horizontal_anchor_point': '1', 'joinstyle': 'bevel', 'offset': '0,-0.40000000000000002',
                'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'outline_color': '35,35,35,255',
                'outline_width': '0', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', 'outline_width_unit': 'MM',
                'size': '4',
                'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'MM', 'vertical_anchor_point': '1'}

    '''
        Symbologie par défaut extraite du style Collaboratif
    '''

    def setModifyWithQgsSingleDefaultSymbolRenderer(self):
        geomType = self.geometryType()
        symbol = None
        color = QColor(f"#{random.randrange(0x1000000):06x}").name(QColor.HexRgb)
        # 'Point'
        if geomType == 0:
            symbol = self.setSymbolPoint(color, color, 0.5)

        # 'Polygon'
        if geomType == 2:
            symbol = self.setSymbolPolygon(color, color, 'solid', '0', 0.5)

        # 'LineString'
        if geomType == 1:
            symbol = self.setSymbolLine(color, 'solid', color, '2', 1)

        if symbol is None:
            symbol = QgsSymbol.defaultSymbol(geomType)
            symbol.setColor(color)
            symbol.setOpacity(1)

        symbol.setOutputUnit(QgsUnitTypes.RenderUnit.RenderPixels)
        renderer = QgsSingleSymbolRenderer(symbol)
        # apply the renderer to the layer
        self.setRenderer(renderer)
        # Refresh layer
        self.triggerRepaint()

    '''
        Symbologie simple extraite du style Collaboratif
    '''

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
                symbol = self.setSymbolPoint(v["fillColor"], v['strokeColor'], 1)

        if symbol is None:
            symbol = QgsSymbol.defaultSymbol(self.geometryType())
            symbol.setColor(QColor('238,153,0,255'))
            symbol.setOpacity(1)

        symbol.setOutputUnit(QgsUnitTypes.RenderUnit.RenderPixels)
        renderer = QgsSingleSymbolRenderer(symbol)
        # apply the renderer to the layer
        self.setRenderer(renderer)
        # Refresh layer
        self.triggerRepaint()

    '''
        Définir la représentation et la direction du symbole en fonction du champ
        strFieldDirection est du genre :
        {"attribute":"sens_de_circulation","sensDirect":"Sens direct","sensInverse":"Sens inverse"}
    '''

    def setPropertySymbol(self, strFieldDirection):
        if strFieldDirection == '':
            return None
        jsonElements = json.loads(strFieldDirection)
        if len(jsonElements) > 3:
            return None
        nameField = jsonElements['attribute']
        direct = jsonElements['sensDirect']
        inverse = jsonElements['sensInverse']
        qgsProperty = QgsProperty()
        qgsProperty.setField(nameField)
        expression = 'CASE WHEN "{}" ='.format(nameField)
        for element in jsonElements:
            if 'attribute' in element:
                continue
            if 'sensDirect' in element:
                expression += '\'{0}\' THEN \'>\' WHEN "{1}" = '.format(direct, nameField)
            if 'sensInverse' in element:
                expression += "'{0}' THEN '<' ELSE '' END".format(inverse)
        if 'END' not in expression:
            return None
        qgsProperty.setExpressionString(expression)
        return qgsProperty

    '''
    Pour appliquer le style collaboratif et les sens de circulation sur les tronçons de route, il faut combiner
    - Ligne
        - Ligne simple
        - Ligne de symboles
            - Symbole
                - Symbole de police
    '''

    def setLineRule(self, expression, valeurs, strFieldDirection):
        if strFieldDirection is None:
            lineSymbol = self.setSymbolLine(valeurs["strokeLinecap"], valeurs["strokeDashstyle"],
                                            valeurs["strokeColor"], str(valeurs["strokeWidth"]),
                                            valeurs['strokeOpacity'])
        else:
            # Ligne
            lineSymbol = QgsLineSymbol()

            # Ligne simple (avec la symbologie issue du collaboratif)
            simpleLineSymbol = QgsSimpleLineSymbolLayer.create(self.setLineStyle(valeurs['strokeLinecap'],
                                                                                 valeurs['strokeDashstyle'],
                                                                                 valeurs['strokeColor'],
                                                                                 valeurs['strokeWidth']))

            # Ligne de symboles (le symbole est appliqué sur le point central du tronçon)
            markerLineSymbol = QgsMarkerLineSymbolLayer.create(self.setSimpleLineSymbolLayer())

            # Symbole
            markerSymlbol = QgsMarkerSymbol()

            # Symbole de police (le caractère >)
            # (appliqué pour un champ, expression appliquée sur le caractère choisi < sens inverse ou sens direct >
            fontMarkerSymbol = QgsFontMarkerSymbolLayer.create(self.setMarkerLineSymbolLayer())
            qgsProperty = self.setPropertySymbol(strFieldDirection)
            if qgsProperty is not None:
                fontMarkerSymbol.setDataDefinedProperty(QgsSymbolLayer.Property.PropertyCharacter, qgsProperty)

            # Remplacement du symbole par défaut
            markerSymlbol.changeSymbolLayer(0, fontMarkerSymbol)
            # Application du symbole caractère sur la ligne de symboles
            markerLineSymbol.setSubSymbol(markerSymlbol)
            # Il faut enlever la ligne simple par défaut
            lineSymbol.deleteSymbolLayer(0)
            # Combinaison ligne simple/ligne de symboles à la ligne
            lineSymbol.appendSymbolLayer(simpleLineSymbol)
            lineSymbol.appendSymbolLayer(markerLineSymbol)
        # Le tout est mis dans une règle nommée contenue dans la variable expression
        ruleBasedRendererLine = QgsRuleBasedRenderer.Rule(lineSymbol, 0, 0, expression, valeurs['name'])
        return ruleBasedRendererLine

    def setPolygonRule(self, expression, valeurs):
        symbolPolygon = self.setSymbolPolygon(valeurs["fillColor"], valeurs['strokeColor'], valeurs['strokeDashstyle'],
                                              str(valeurs['strokeWidth']), valeurs['fillOpacity'])
        ruleBasedRendererPolygon = QgsRuleBasedRenderer.Rule(symbolPolygon, 0, 0, expression, valeurs['name'])
        return ruleBasedRendererPolygon

    def setPointRule(self, expression, valeurs):
        symbolPoint = self.setSymbolPoint(valeurs["fillColor"], valeurs['strokeColor'], 1)
        ruleBasedRendererPoint = QgsRuleBasedRenderer.Rule(symbolPoint, 0, 0, expression, valeurs['name'])
        return ruleBasedRendererPoint

    '''
        Symbologie avec règles extraite du style Collaboratif
    '''

    def setModifyWithQgsRuleBasedSymbolRenderer(self, data, bExpression):
        # Rule (QgsSymbol *symbol, int maximumScale=0, int minimumScale=0, const QString &filterExp=QString(),
        # const QString &label=QString(), const QString &description=QString(), bool elseRule=false)
        strDirectionField = None
        if 'default' in data:
            strDirectionField = data['default']['directionField']
        rules = []
        for c, v in data.items():
            expression = self.changeConditionToExpression(v['condition'], bExpression)
            if v['type'] == 'line':
                lineRule = self.setLineRule(expression, v, strDirectionField)
                rules.append(lineRule)
            if v['type'] == 'polygon':
                polygonRule = self.setPolygonRule(expression, v)
                rules.append(polygonRule)
            if v['type'] == 'point':
                pointRule = self.setPointRule(expression, v)
                rules.append(pointRule)

        # create a new rule-based renderer
        symbol = QgsSymbol.defaultSymbol(self.geometryType())
        renderer = QgsRuleBasedRenderer(symbol)

        # get the "root" rule
        root_rule = renderer.rootRule()
        for rule in rules:
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
            0: 559082264,
            1: 279541132,
            2: 139770566,
            3: 69885283,
            4: 34942642,
            5: 17471321,
            6: 8735660,
            7: 4367830,
            8: 2183915,
            9: 1091958,
            10: 545979,
            11: 272989,
            12: 136495,
            13: 68247,
            14: 34124,
            15: 17062,
            16: 8531,
            17: 4265,
            18: 2133,
            19: 1066,
            20: 533,
            21: 267
        }
        self.setMinimumScale(scale[minS])
        self.setMaximumScale(scale[maxS])
        self.setScaleBasedVisibility(True)
