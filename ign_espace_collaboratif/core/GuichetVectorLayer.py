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
    QgsFontMarkerSymbolLayer, QgsSymbolLayer, QgsProperty, Qgis

from .MongoDBtoQGIS.ConditionFactory import ConditionFactory


class GuichetVectorLayer(QgsVectorLayer):
    """
    Classe dérivée de QgsVectorLayer pour une couche extraite à partir de l'espace collaboratif. Elle définit
    les paramètres pour :
     - le lien de connexion avec la base SQLite du projet,
     - la symbologie des objets qui la composent,
     - envoyer vers le serveur les données mises à jour.

     NB : pour retrouver un style graphique de QGIS, il faut lancer une commande dans la fenêtre Python de QGIS. Ce sont
     ces retours de styles qui sont appliqués dans les fonctions de la classe.

     Exemples :
      - Ligne simple pour la couche BDUni 'troncon_de_route' :
     Sans règle : print(QgsProject.instance().mapLayersByName("troncon_de_route")[0].renderer().
     symbols(QgsRenderContext())[13].symbolLayers()[0].properties())

      - Symbole de police pour la couche BDUni 'troncon_de_route' :
    Sans règle : print(QgsProject.instance().mapLayersByName("troncon_de_route")[0].renderer().
    symbols(QgsRenderContext())[13].symbolLayers()[1].subSymbol()[0].properties())QgsFontMarkerSymbolLayer
    Avec règle : print(QgsProject.instance().mapLayersByName("troncon_de_route")[0].renderer().rootRule().
    children()[13].symbols(QgsRenderContext())[0].symbolLayers()[1].subSymbol()[0].properties())

     - Ligne de symboles pour la couche BDUni 'troncon_de_route' :
     print(QgsProject.instance().mapLayersByName("troncon_de_route")[0].renderer().symbols(QgsRenderContext())[13]
     .symbolLayers()[1].properties())

     - etc... Avec un peu de patience et de recherches, les styles sont 'facilement' retrouvables.
    """

    def __init__(self, parameters) -> None:
        """
        Constructeur.

        :param parameters: les données nécessaires pour l'extraction de la couche, sa réprésentation graphique
                           et sa mise à jour
        :type parameters: dict
        """
        super().__init__(parameters['uri'], parameters['name'], parameters['genre'])
        self.databasename = parameters['databasename']
        self.sqliteManager = parameters['sqliteManager']
        self.srid = -1
        self.isStandard = True
        self.idNameForDatabase = parameters['idName']
        self.geometryNameForDatabase = parameters['geometryName']
        self.geometryDimensionForDatabase = parameters['geometryDimension']
        self.geometryTypeForDatabase = parameters['geometryType']
        self.conditionFactory = ConditionFactory()
        self.__name = parameters['name']

    def name(self) -> str:
        """
        :return: le nom de la couche
        """
        return self.__name

    def __changeConditionToExpression(self, condition, bExpression) -> str:
        """
        Transformation d'une condition Espace collaboratif en expression QGIS.
        La condition '{"$and" : [{"zone" : "Zone1"}]}' doit devenir '"zone" LIKE \"Zone1\"'
        et doit se traduire dans QGIS par "zone" LIKE 'Zone1'

        :param condition: une condition
        :type condition: str

        :param bExpression: à True pour ajouter un ELSE en fin d'expression dans le cas de plusieurs conditions
                            à paramétrer
        :type bExpression: bool
        TODO : manque le traitement du AND, OR, etc...
        """
        # Pas de style pour la couche, style QGIS par défaut
        if bExpression is False and condition is None or condition == '':
            return ''
        # Pas de rule style, capture de toutes les autres entités
        if bExpression is True and condition is None:
            return "ELSE"
        expression = self.conditionFactory.create_condition(condition)
        return expression.toSQL()

    def __setPointStyle(self, fillColor, strokeColor) -> dict:
        """
        Défini pour QGIS une représentation graphique d'un point en transformant le style issu du collaboratif.

        :param fillColor: couleur de remplissage
        :type fillColor: str

        :param strokeColor: couleur du trait entourant le symbole
        :type strokeColor: str

        :return: un style par défaut pour un point
        """
        return {'angle': '0', 'color': fillColor, 'horizontal_anchor_point': '1',
                'joinstyle': 'round', 'name': 'circle', 'offset': '0,0',
                'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                'outline_color': strokeColor, 'outline_style': 'solid',
                'outline_width': '2', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0',
                'outline_width_unit': 'Pixel', 'scale_method': 'diameter', 'size': '10',
                'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'Pixel',
                'vertical_anchor_point': '1'}

    def __setLineStyle(self, strokeDashstyle, strokeColor, strokeWidth) -> dict:
        """
        Applique une représentation graphique à une ligne. Plusieurs représentations graphiques sont définies
        en transformant les styles issus du collaboratif en styles QGIS. Ainsi plusieurs styles sont définis :
         - 'solid' (Ligne continu → trait continu)
         - 'dash' (Ligne en tiret → traits courts)
         - 'dot' (Ligne en pointillé → points)
         - 'dashdot' (Ligne tiret-point → points/traits courts)
         - 'longdashdot' (Ligne tiret-point-point → points/traits longs)
         - 'longdash' (Ligne en tiret → traits longs)

        :param strokeDashstyle: style de trait
        :type strokeDashstyle: str

        :param strokeColor: couleur du trait bordant la ligne
        :type strokeColor: str

        :param strokeWidth: taille de trait bordant la ligne
        :type strokeWidth: str

        :return : le style d'une ligne en fonction de la variable 'strokeDashStyle' donnée en entrée
        """
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
            # Ligne continu → trait continu
            'solid': {'capstyle': 'solid', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                      'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                      'line_color': strokeColor, 'line_style': 'solid', 'line_width': strokeWidth,
                      'line_width_unit': 'Pixel',
                      'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                      'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne en tiret → traits courts
            'dash': {'capstyle': 'dash', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                     'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                     'line_color': strokeColor, 'line_style': 'dash', 'line_width': strokeWidth,
                     'line_width_unit': 'Pixel',
                     'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                     'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne en pointillé → points
            'dot': {'capstyle': 'dot', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                    'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                    'line_color': strokeColor, 'line_style': 'dot', 'line_width': strokeWidth,
                    'line_width_unit': 'Pixel',
                    'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                    'ring_filter': '0', 'use_custom_dash': '0', 'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne tiret-point → points/traits courts
            'dashdot': {'capstyle': 'dash dot', 'customdash': '5;2', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                        'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                        'line_color': strokeColor, 'line_style': 'dash dot', 'line_width': strokeWidth,
                        'line_width_unit': 'Pixel', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0',
                        'offset_unit': 'Pixel', 'ring_filter': '0', 'use_custom_dash': '0',
                        'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne tiret-point-point → points/traits longs
            'longdashdot': {'capstyle': 'dash dot dot', 'customdash': '10;5',
                            'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                            'customdash_unit': 'Pixel', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                            'line_color': strokeColor, 'line_style': 'dash dot dot', 'line_width': strokeWidth,
                            'line_width_unit': 'Pixel', 'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0',
                            'offset_unit': 'Pixel', 'ring_filter': '0', 'use_custom_dash': '0',
                            'width_map_unit_scale': '3x:0,0,0,0,0,0'},
            # Ligne en tiret → traits longs
            'longdash': {'capstyle': 'dash', 'customdash': '10;5', 'customdash_map_unit_scale': '3x:0,0,0,0,0,0',
                         'customdash_unit': 'Point', 'draw_inside_polygon': '0', 'joinstyle': 'round',
                         'line_color': strokeColor, 'line_style': 'no', 'line_width': strokeWidth,
                         'line_width_unit': 'Pixel',
                         'offset': '0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Pixel',
                         'ring_filter': '0', 'use_custom_dash': '1', 'width_map_unit_scale': '3x:0,0,0,0,0,0'}
        }
        return lineStyles[strokeDashstyle]

    def __setPolygonStyle(self, fillColor, strokeColor, strokeDashstyle, strokeWidth) -> dict:
        """
        Applique une représentation graphique à un polygone. Plusieurs représentations graphiques sont définies pour
        le style de trait entourant le polygone en transformant les styles issus du collaboratif en styles QGIS.
        Ainsi plusieurs styles sont définis :
         - 'solid' (Ligne continu → trait continu)
         - 'dash' (Ligne en tiret → traits courts)
         - 'dot' (Ligne en pointillé → points)
         - 'dashdot' (Ligne tiret-point → points/traits courts)
         - 'longdashdot' (Ligne tiret-point-point → points/traits longs)
         - 'longdash' (Ligne en tiret → traits longs)

        :param fillColor: couleur de remplissage
        :type fillColor: str

        :param strokeColor: couleur du trait entourant le polygone
        :type strokeColor: str

        :param strokeDashstyle: style de trait
        :type strokeDashstyle: str

        :param strokeWidth: taille de trait entourant le polygone
        :type strokeWidth: str

        :return: le style d'un polygone en fonction de la variable 'strokeDashStyle' donnée en entrée
        """
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

    def __setSymbolPoint(self, fillColor, strokeColor, fillOpacity) -> QgsMarkerSymbol:
        """
        Applique une représentation graphique à un point.

        :param fillColor: couleur de remplissage
        :type fillColor: str

        :param strokeColor: couleur du trait entourant le symbole
        :type strokeColor: str

        :param fillOpacity: opacité de la couleur de remplissage
        :type fillOpacity: float

        :return: la symbologie appliquée à un point
        """
        if fillColor is None:
            fillColor = QColor(f"#{random.randrange(0x1000000):06x}").name(QColor.HexRgb)
        if strokeColor is None:
            strokeColor = QColor(f"#{random.randrange(0x1000000):06x}").name(QColor.HexRgb)
        if fillOpacity is None:
            fillOpacity = 1
        pointSymbol = self.__setPointStyle(fillColor, strokeColor)
        symbol = QgsMarkerSymbol().createSimple(pointSymbol)
        symbol.setOpacity(fillOpacity)
        return symbol

    # Example
    # 'fillColor': None,
    # 'fillOpacity': None,
    # 'fillPattern': None,
    # 'patternColor': None,
    # 'strokeColor': '#a18552',
    # 'strokeBorderColor': None,
    # 'strokeOpacity': 1.0,
    # 'strokeWidth': 7,
    # 'strokeLinecap': 'square',
    # 'strokeDashstyle': 'dash',
    def __setSymbolLine(self, strokeDashstyle, strokeColor, strokeWidth, strokeOpacity) -> QgsLineSymbol:
        """
        Applique une représentation graphique à une ligne.

        :param strokeDashstyle: style de trait
        :type strokeDashstyle: str

        :param strokeColor: couleur du trait bordant la ligne
        :type strokeColor: str

        :param strokeWidth: taille de trait bordant la ligne
        :type strokeWidth: str

        :param strokeOpacity: opacité de la couleur de la ligne
        :type strokeOpacity: float

        :return: la symbologie appliquée à une ligne
        """
        lineSymbol = self.__setLineStyle(strokeDashstyle, strokeColor, strokeWidth)
        symbol = QgsLineSymbol().createSimple(lineSymbol)
        symbol.setOpacity(strokeOpacity)
        return symbol

    def __setSymbolPolygon(self, fillColor, strokeColor, strokeDashstyle, strokeWidth, fillOpacity) -> QgsFillSymbol:
        """
        Applique une représentation graphique à un polygone.

        :param fillColor: couleur de remplissage
        :type fillColor: str

        :param strokeColor: couleur du trait entourant le polygone
        :type strokeColor: str

        :param strokeDashstyle: style de trait
        :type strokeDashstyle: str

        :param strokeWidth: taille de trait entourant le polygone
        :type strokeWidth: str

        :param fillOpacity: taille de trait entourant le polygone
        :type fillOpacity: float

        :return: le style d'un polygone en fonction de la variable 'strokeDashStyle' donnée en entrée
        """
        polygonSymbol = self.__setPolygonStyle(fillColor, strokeColor, strokeDashstyle, strokeWidth)
        symbol = QgsFillSymbol().createSimple(polygonSymbol)
        symbol.setOpacity(fillOpacity)
        return symbol

    def __setSimpleLineSymbolLayer(self):
        return {'average_angle_length': '4', 'average_angle_map_unit_scale': '3x:0,0,0,0,0,0',
                'average_angle_unit': 'MM',
                'interval': '3', 'interval_map_unit_scale': '3x:0,0,0,0,0,0', 'interval_unit': 'MM', 'offset': '0',
                'offset_along_line': '0', 'offset_along_line_map_unit_scale': '3x:0,0,0,0,0,0',
                'offset_along_line_unit': 'MM',
                'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'placement': 'centralpoint',
                'ring_filter': '0',
                'rotate': '1'}

    def __setMarkerLineSymbolLayer(self):
        return {'angle': '0', 'chr': '>', 'color': '0,0,0,255', 'font': 'Arial', 'font_style': 'Normal',
                'horizontal_anchor_point': '1', 'joinstyle': 'bevel', 'offset': '0,-0.40000000000000002',
                'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'outline_color': '35,35,35,255',
                'outline_width': '0', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', 'outline_width_unit': 'MM',
                'size': '4',
                'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'MM', 'vertical_anchor_point': '1'}

    def __setModifyWithQgsSingleDefaultSymbolRenderer(self) -> None:
        """
        Défini une symbologie par défaut pour les trois types de couches (point, ligne, surface).
        """
        geomType = self.geometryType()
        symbol = None
        color = QColor(f"#{random.randrange(0x1000000):06x}").name(QColor.HexRgb)
        # 'Point'
        if geomType == 0:
            symbol = self.__setSymbolPoint(color, color, 0.5)

        # 'Polygon'
        if geomType == 2:
            symbol = self.__setSymbolPolygon(color, color, 'solid', '0', 0.5)

        # 'LineString'
        if geomType == 1:
            symbol = self.__setSymbolLine('solid', color, '2', 1)

        if symbol is None:
            symbol = QgsSymbol.defaultSymbol(geomType)
            symbol.setColor(color)
            symbol.setOpacity(1)

        symbol.setOutputUnit(Qgis.RenderUnit.Pixels)
        renderer = QgsSingleSymbolRenderer(symbol)
        # apply the renderer to the layer
        self.setRenderer(renderer)
        # Refresh layer
        self.triggerRepaint()

    def __setModifyWithQgsSingleSymbolRenderer(self, data) -> None:
        """
        Défini une symbologie simple extraite du style Collaboratif.

        :param data: les données de symbologie
        :tupe data: dict
        """
        symbol = None
        for c, v in data.items():

            if v['type'] == 'line':
                symbol = self.__setSymbolLine(v["strokeDashstyle"], v["strokeColor"],
                                              str(v["strokeWidth"]), v['strokeOpacity'])

            if v['type'] == 'polygon':
                symbol = self.__setSymbolPolygon(v["fillColor"], v['strokeColor'], v['strokeDashstyle'],
                                                 str(v['strokeWidth']),
                                                 v['fillOpacity'])

            if v['type'] == 'point':
                symbol = self.__setSymbolPoint(v["fillColor"], v['strokeColor'], v['fillOpacity'])

        if symbol is None:
            symbol = QgsSymbol.defaultSymbol(self.geometryType())
            symbol.setColor(QColor('238,153,0,255'))
            symbol.setOpacity(1)

        symbol.setOutputUnit(Qgis.RenderUnit.Pixels)
        renderer = QgsSingleSymbolRenderer(symbol)
        # apply the renderer to the layer
        self.setRenderer(renderer)
        # Refresh layer
        self.triggerRepaint()

    def __setPropertySymbol(self, strFieldDirection):
        """
        Défini la représentation et la direction du symbole en fonction du champ.

        :param strFieldDirection: de genre {"attribute":"sens_de_circulation","sensDirect":"Sens direct",
                                  "sensInverse":"Sens inverse"}
        :type strFieldDirection: str
        """
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

    def __setLineRule(self, expression, valeurs, strFieldDirection) -> QgsRuleBasedRenderer.Rule:
        """
        Applique une règle de symbologie à une ligne.
        NB : une condition de l'espace collaboratif est transformée en expression QGIS.
        NB : Pour appliquer le style collaboratif et les sens de circulation sur les tronçons de route,
        il faut combiner :
         Ligne
          Ligne simple
           Ligne de symboles
            Symbole
             Symbole de police

        :param expression: la condition d'affichage de la symbologie
        :type expression: str

        :param valeurs: les valeurs de symbologie
        :type valeurs: dict

        :param strFieldDirection: le sens donné à l'attribut par rapport au sens de saisie de l'objet
                                  (un sens de circulation peut-être direct ou inverse)
        :type strFieldDirection: str

        :return: la règle de symbologie de la ligne
        """
        otherLineSymbol = None
        strokeWidth = valeurs['strokeWidth']
        # Représentation d'une route à deux traits
        if (valeurs['strokeBorderColor']) is not None:
            otherLineSymbol = QgsSimpleLineSymbolLayer.create(self.__setLineStyle(valeurs['strokeDashstyle'],
                                                                                  valeurs['strokeBorderColor'],
                                                                                  strokeWidth + 2))
            strokeWidth = strokeWidth - 2

        if strFieldDirection is None:
            lineSymbol = self.__setSymbolLine(valeurs["strokeDashstyle"], valeurs["strokeColor"],
                                              str(strokeWidth), valeurs['strokeOpacity'])
        else:
            # Ligne
            lineSymbol = QgsLineSymbol()

            # Ligne simple (avec la symbologie issue du collaboratif)
            simpleLineSymbol = QgsSimpleLineSymbolLayer.create(self.__setLineStyle(valeurs['strokeDashstyle'],
                                                                                   valeurs['strokeColor'], strokeWidth))
            # Ligne de symboles (le symbole est appliqué sur le point central du tronçon)
            markerLineSymbol = QgsMarkerLineSymbolLayer.create(self.__setSimpleLineSymbolLayer())

            # Symbole
            markerSymlbol = QgsMarkerSymbol()

            # Symbole de police (le caractère >)
            # (appliqué pour un champ, expression appliquée sur le caractère choisi < sens inverse ou sens direct >
            fontMarkerSymbol = QgsFontMarkerSymbolLayer.create(self.__setMarkerLineSymbolLayer())
            qgsProperty = self.__setPropertySymbol(strFieldDirection)
            if qgsProperty is not None:
                fontMarkerSymbol.setDataDefinedProperty(QgsSymbolLayer.Property.Character, qgsProperty)

            # Remplacement du symbole par défaut
            markerSymlbol.changeSymbolLayer(0, fontMarkerSymbol)
            # Application du symbole caractère sur la ligne de symboles
            markerLineSymbol.setSubSymbol(markerSymlbol)
            # Il faut enlever la ligne simple par défaut
            lineSymbol.deleteSymbolLayer(0)
            # Combinaison ligne simple/ligne de symboles à la ligne
            if otherLineSymbol is not None:
                lineSymbol.appendSymbolLayer(otherLineSymbol)
            lineSymbol.appendSymbolLayer(simpleLineSymbol)
            lineSymbol.appendSymbolLayer(markerLineSymbol)
        # Le tout est mis dans une règle nommée contenue dans la variable expression
        ruleBasedRendererLine = QgsRuleBasedRenderer.Rule(lineSymbol, 0, 0, expression, valeurs['name'])
        return ruleBasedRendererLine

    def __setPolygonRule(self, expression, valeurs) -> QgsRuleBasedRenderer.Rule:
        """
        Applique une règle de symbologie à un polygone.
        NB : une condition de l'espace collaboratif est transformée en expression QGIS.

        :param expression: la condition d'affichage de la symbologie
        :type expression: str

        :param valeurs: les valeurs de symbologie
        :type valeurs: dict

        :return: la règle de symbologie du polygone
        """
        symbolPolygon = self.__setSymbolPolygon(valeurs["fillColor"], valeurs['strokeColor'],
                                                valeurs['strokeDashstyle'], str(valeurs['strokeWidth']),
                                                valeurs['fillOpacity'])
        ruleBasedRendererPolygon = QgsRuleBasedRenderer.Rule(symbolPolygon, 0, 0, expression, valeurs['name'])
        return ruleBasedRendererPolygon

    def __setPointRule(self, expression, valeurs) -> QgsRuleBasedRenderer.Rule:
        """
        Applique une règle de symbologie à un point.
        NB : une condition de l'espace collaboratif est transformée en expression QGIS.

        :param expression: la condition d'affichage de la symbologie
        :type expression: str

        :param valeurs: les valeurs de symbologie
        :type valeurs: dict

        :return: la règle de symbologie du point
        """
        symbolPoint = self.__setSymbolPoint(valeurs["fillColor"], valeurs['strokeColor'], valeurs['fillOpacity'])
        ruleBasedRendererPoint = QgsRuleBasedRenderer.Rule(symbolPoint, 0, 0, expression, valeurs['name'])
        return ruleBasedRendererPoint

    def __setModifyWithQgsRuleBasedSymbolRenderer(self, data, bExpression) -> None:
        """
        Applique un ensemble de règles de symbologie extraites du style collaboratif.
        Une règle au sens QGIS est définie comme suit :
        Rule (QgsSymbol *symbol, int maximumScale=0, int minimumScale=0, const QString &filterExp=QString(),
        const QString &label=QString(), const QString &description=QString(), bool elseRule=false)

        :param data: les données de symbologie
        :type data: dict

        :param bExpression: à True, si plusieurs conditions d'affichage sont à transformer en expression.
                            Chaque expression sera séparée par un ELSE.
        :type bExpression: bool
        """
        strDirectionField = None
        if 'default' in data:
            strDirectionField = data['default']['directionField']
        rules = []
        for c, v in data.items():
            expression = self.__changeConditionToExpression(v['condition'], bExpression)
            if v['type'] == 'line':
                lineRule = self.__setLineRule(expression, v, strDirectionField)
                rules.append(lineRule)
            if v['type'] == 'polygon':
                polygonRule = self.__setPolygonRule(expression, v)
                rules.append(polygonRule)
            if v['type'] == 'point':
                pointRule = self.__setPointRule(expression, v)
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

    def setModifySymbols(self, listOfValues) -> None:
        """
        Applique une symbologie (listOfValues) à une couche.

        :param listOfValues: liste de la (ou des) symbologie(s)
        :type listOfValues: dict
        """

        # Pas de balise Style, Symbologie = Symbole QGIS par défaut
        if len(listOfValues) == 0:
            self.__setModifyWithQgsSingleDefaultSymbolRenderer()

        # Une balise Style, Symbologie = Symbole unique
        if len(listOfValues) == 1:
            self.__setModifyWithQgsSingleSymbolRenderer(listOfValues)

        # Balise Style avec balise(s) Children, Symbologie = Ensemble de règles
        if len(listOfValues) > 1:
            self.__setModifyWithQgsRuleBasedSymbolRenderer(listOfValues, True)

    def setDisplayScale(self, minS, maxS) -> None:
        """
        Applique une échelle minimum et maximum pour l'affichage suite à la création d'une couche dans QGIS.
        Source : https://geoservices.ign.fr/documentation/geoservices/wmts.html#taille-des-tuiles-en-pixels

        :param minS: échelle minimum
        :type minS: int

        :param maxS: échelle maximum
        :type maxS: int
        """
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
