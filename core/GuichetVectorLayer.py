import random

from PyQt5.QtGui import QColor
from qgis.core import QgsVectorLayer, QgsProject, QgsEditorWidgetSetup, QgsSymbol, QgsFeatureRenderer,\
    QgsRuleBasedRenderer, QgsSingleSymbolRenderer, QgsLineSymbol, QgsFillSymbol, QgsMarkerSymbol, QgsUnitTypes
from .Statistics import Statistics
import hashlib
import os

class GuichetVectorLayer(QgsVectorLayer):
    # Les statistiques de comptage pour la couche
    stat = None

    # La liste des id/md5 par objet AVANT le travail de l'utilisateur
    md5BeforeWorks = []

    # La liste des id/md5 par objet APRES le travail de l'utilisateur
    md5AfterWorks = []

    # Les fichiers ou sont stockés les objets
    repertoire = None
    fileBeforeWorks = None
    fileAfterWorks = None



    def getStat(self):
        return self.stat



    def openFile(self, nameFile, mode):
        file = open(nameFile, mode)
        return file



    def closeFile(self, fileToClose):
        fileToClose.close()



    '''
    Connexion des signaux
    Initialisation des comptages
    '''
    def __init__(self, projectDirectory, layerName, layerType):

        super(GuichetVectorLayer, self).__init__(projectDirectory, layerName, layerType)
        self.connectSignals()
        self.stat = Statistics(self.featureCount())
        self.repertoire = projectDirectory
        fileName = QgsProject.instance().fileName()
        tmp = fileName.replace(".qgz", "")
        nodeGroups = QgsProject.instance().layerTreeRoot().findGroups()
        self.fileAfterWorks = "{}{}{}_{}".format(tmp, nodeGroups[0].name(), layerName, "md5AfterWorks.txt")
        self.fileBeforeWorks = "{}{}{}_{}".format(tmp, nodeGroups[0].name(), layerName, "md5BeforeWorks.txt")



    '''
    Connexion des signaux pour les évènements survenus sur la carte
    '''
    def connectSignals(self):
        # self.geometryChanged.connect(self.geometry_changed)
        # self.attributeValueChanged.connect(self.attribute_value_changed)
        # self.featureAdded.connect(self.feature_added)
        # self.featuresDeleted.connect(self.features_deleted)
        self.attributeAdded.connect(self.attribute_added)
        self.attributeDeleted.connect(self.attribute_deleted)
        self.editingStopped.connect(self.editing_stopped)



    '''
    Calcul d'une clé de hachage à partir des caractéristiques d'un objet
    # géométrie et valeurs de ses attributs
    '''
    def setMD5(self, feature):
        allAttributes = []

        # Ajout de la géometrie
        allAttributes.append("{}".format(feature.geometry().asJson()))

        # Ajout de la liste des valeurs d'attributs
        listValues = feature.attributes()
        for value in listValues:
            allAttributes.append("{}".format(value))

        # Concaténation et encodage des valeurs d'attributs
        tmp = "".join(allAttributes).encode('utf-8')

        # Calcul de la clé
        cle = hashlib.sha224(tmp).hexdigest()

        # Retourne la référence par objet (idQGIS:MD5)
        '''fields = self.fields()
        id = None
        for field in fields:
            name = field.name()
            if name != 'id':
                continue

            index = fields.indexOf(name)
            if index == -1:
                id = feature.id()
            else:
                value = feature.attribute(index)
                # l'id est rempli
                if value > 0:
                    id = value
                # l'id existe mais n'est pas remplie, valeur = NULL
                else:
                    id = feature.id()

        # si l'objet n'a pas d'attribut id
        if id is None:
            id = feature.id()'''

        return (feature.id(), cle)



    '''
    Au chargement de la couche dans QGIS, les caractéristiques des objets initiaux
    sont stockées dans un fichier sous la forme d'une clé de hachage :
    id QGIS/clé de hachage
    '''
    def setMd5BeforeWorks(self):
        # il faut détruire le fichier afterWorks
        if os.path.exists(self.fileAfterWorks):
            os.remove(self.fileAfterWorks)

        fichier = self.openFile(self.fileBeforeWorks, "wt")
        features = self.getFeatures()
        for feature in features:
            id_cle = self.setMD5(feature)
            self.md5BeforeWorks.append(id_cle)
            fichier.write("{}:{}{}".format(id_cle[0], id_cle[1], "\n"))
        self.closeFile(fichier)



    '''
    Dès la fin de l'édition d'une couche, les caractéristiques des objets
    sont stockées dans un fichier sous la forme d'une clé de hachage :
    id QGIS/clé de hachage
    Il doit y avoir des objets créés, modifiés, supprimés
    '''
    def setMd5AfterWorks(self):
        fichier = self.openFile(self.fileAfterWorks, "wt")
        features = self.getFeatures()
        for feature in features:
            id_cle = self.setMD5(feature)
            self.md5AfterWorks.append(id_cle)
            fichier.write("{}:{}{}".format(id_cle[0], id_cle[1], "\n"))
        self.closeFile(fichier)



    '''
    L'utilisateur a mis fin à l'édition de la couche,
    les objets sont stockés dans un fichier
    '''
    def editing_stopped(self):
        self.setMd5AfterWorks()



    '''
    Interdiction de supprimer un attribut sinon la synchronisation au serveur est perdue
    '''
    def attribute_deleted(self, idx):
        fields = self.fields()
        raise Exception("Impossible de supprimer l'attribut {} car la synchronisation au serveur sera perdue.".format(fields[idx].name()))



    '''
    Interdiction d'ajouter un attribut sinon la synchronisation au serveur est perdue
    '''
    def attribute_added(self, idx):
        fields = self.fields()
        raise Exception("Impossible d'ajouter l'attribut {} car la synchronisation au serveur sera perdue.".format(fields[idx].name()))



    '''
    Comptage par différentiel des objets
    ajoutés, supprimés ou modifiés de la couche
    '''
    def doDifferentielAfterBeforeWorks(self):
        # Ajout
        self.stat.nfa = 0
        # Suppression
        self.stat.nfd = 0
        # Modification
        self.stat.nfc = 0

        # Dictionnaire cle/valeur carte origine
        before = self.openFile(self.fileBeforeWorks, "r")
        lines = before.readlines()
        dictBefore = {}
        for line in lines:
            tmp = line.split(":")
            dictBefore[tmp[0]] = tmp[1]
        self.closeFile(before)

        # oublie de sauvegarder le projet : pas de fichier after
        if not os.path.exists(self.fileAfterWorks):
            return

        # Dictionnaire cle/valeur carte après intervention utilisateur
        after = self.openFile(self.fileAfterWorks, "r")
        lines = after.readlines()
        dictAfter = {}
        for line in lines:
            tmp = line.split(":")
            dictAfter[tmp[0]] = tmp[1]
        self.closeFile(after)

        '''
        Différentiel entre les deux dictionnaires
        '''
        # Ajout/modification d'éléments
        for cle, md5 in dictAfter.items():
            if cle not in dictBefore:
                print("feature {} ajouté".format(cle))
                self.stat.nfa += 1
            else:
                if md5 != dictBefore[cle]:
                    print("feature {} : modifié".format(cle))
                    self.stat.nfc += 1

        # Suppression d'éléments
        for cle, md5 in dictBefore.items():
            if cle not in dictAfter:
                print("feature {} : supprimé".format(cle))
                self.stat.nfd += 1



    '''
    Modification du formulaire de saisie pour afficher la liste de valeurs de certains attributs "liste"
    [Layer:Propriétés][Bouton:Formulaire d'attributs][Fenêtre:Contrôles disponibles][Onglet:Fields]
    Exemple : config = {'map': [{'':'', 'Zone1': 'Zone1'},{' Zone2': ' Zone2'}, {'Zone3': 'Zone3'}]}
    '''
    def setModifyFormAttributes(self, listOfValues):
        fields = self.fields()
        attribute_values = {}
        for attribute, values in listOfValues.items():
            QgsEWS_type = 'ValueMap'
            index = fields.indexOf(attribute)

            if type(values) is list:
                attribute_values.clear()
                for value in values:
                    attribute_values[value] = value

            if type(values) is dict:
                attribute_values.clear()
                for cle, value in values.items():
                    attribute_values[cle] = value

            QgsEWS_config = {'map': attribute_values}
            setup = QgsEditorWidgetSetup(QgsEWS_type, QgsEWS_config)
            self.setEditorWidgetSetup(index, setup)



    '''
        Transformation de la condition en expression QGIS
        La condition '{"$and" : [{"zone" : "Zone1"}]}' doit devenir '"zone" LIKE \"Zone1\"'
        et doit se traduire dans QGIS par "zone" LIKE 'Zone1'
        TODO : manque le traitement du AND, OR, etc...
    '''
    def changeConditionToExpression(self, condition, bExpression):
        # Pas de style pour la couche, style QGIS par défaut
        if bExpression is False and condition is None:
            return ''

        #Pas de rule style, capture de toutes les autres entités
        if bExpression is True and condition is None:
            return "ELSE"

        if type(condition) is str:
            c = condition.replace(' ','')
            c1 = c.replace('"', '')
            tmp = c1.split(':')
            attribute = tmp[1].replace('[{', '')
            value = tmp[2].replace('}]}', '')
            return "\"{}\" LIKE \'{}\'".format(attribute, value)

        return ''



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
                symbol = self.setSymbolPolygon(v["fillColor"], v['strokeColor'], v['strokeDashstyle'], str(v['strokeWidth']),
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



    def setModifyWithQgsRuleBasedSymbolRendererTer(self, data, bExpression):
        # class_rules = ('label=name', 'expression=condition', 'color=fillColor/strokeColor', 'opacity=fillOpacity/strokeOpacity' )
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
                rule.symbol().setWidth(width)
            # append the rule to the list of rules
            root_rule.appendChild(rule)

        # delete the default rule
        root_rule.removeChildAt(0)

        # apply the renderer to the layer
        self.setRenderer(renderer)
        # Refresh layer
        self.triggerRepaint()



    def setModifyWithQgsRuleBasedSymbolRendererBis(self, data, bExpression):
        isTypePoint = False
        class_rules = []
        #symbol = None
        for c, v in data.items():
            tmp = [v['name']]
            tmp.append(v['type'])
            if v['type'] == 'line':
                symbol = self.setSymbolLine(v["strokeLinecap"], v["strokeDashstyle"], v["strokeColor"],
                                            str(v["strokeWidth"]), v['strokeOpacity'])
                tmp.append(symbol)

            if v['type'] == 'polygon':
                symbol = self.setSymbolPolygon(v["fillColor"], v['strokeColor'], v['strokeDashstyle'],
                                               str(v['strokeWidth']), v['fillOpacity'])
                tmp.append(symbol)

            if v['type'] == 'point':
                fillcolor = v["fillColor"]
                if fillcolor is None:
                    fillcolor = QColor("0,0,0,255")
                    isTypePoint = True
                strokecolor = v['strokeColor']
                if strokecolor is None:
                    strokecolor = QColor("0,0,0,255")
                    isTypePoint = True
                symbol = self.setSymbolPoint(fillcolor, strokecolor)
                tmp.append(symbol)

            expression = self.changeConditionToExpression(v['condition'], bExpression)
            tmp.append(expression)
            class_rules.append(tmp)
        # create a new rule-based renderer
        renderer = QgsRuleBasedRenderer()
        for label, symbol, expression in class_rules:
            renderer.setSymbol (symbol)
            # get the "root" rule
            root_rule = renderer.rootRule()
            # create a clone (i.e. a copy) of the default rule
            rule = root_rule.children()[0].clone()
            # set the label, opacity, expression and color
            rule.setLabel(label)
            rule.setFilterExpression(expression)
            rule.symbol().setOutputUnit(QgsUnitTypes.RenderPixels)
            # Remplacement des symboles
            if isTypePoint:
                rule.symbol().setColor(QColor(f"#{random.randrange(0x1000000):06x}"))
            # append the rule to the list of rules
            root_rule.appendChild(rule)
            # delete the default rule
            root_rule.removeChildAt(0)

        # apply the renderer to the layer
        self.setRenderer(renderer)

        # Refresh layer
        self.triggerRepaint()



    def setModifyWithQgsRuleBasedSymbolRenderer(self, data, bExpression):
        # class_rules = ('label=name', 'expression=condition', 'color=fillColor/strokeColor', 'opacity=fillOpacity/strokeOpacity' )
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




    def appendClassRules(self, data, bExpression):
        # class_rules = (
        # 'label=name',
        # 'expression=condition',
        # 'color=fillColor/strokeColor',
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
            # Ajout de la symbologie 'Ensemble de règles' pour une couche
            class_rules.append(tmp)

        return class_rules



    def setModifyWithQgsRuleBasedSymbolRendererQuater(self, data, bExpression):
        # class_rules = ('label=name', 'expression=condition', 'color=fillColor/strokeColor', 'opacity=fillOpacity/strokeOpacity' )
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
            #rule.symbol().setFillColor(fillColor)
            #rule.symbol().setStrokeColor(strokeColor)
            #rule.symbol().setPenCapStyle(capStyle)
            rule.symbol().setOpacity(opacity)
            rule.symbol().setOutputUnit(QgsUnitTypes.RenderPixels)
            if width != '':
                rule.symbol().setWidth(width)
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
        bExpression = False
        if len(listOfValues) > 1:
            bExpression = True
            self.setModifyWithQgsRuleBasedSymbolRenderer(listOfValues, bExpression)