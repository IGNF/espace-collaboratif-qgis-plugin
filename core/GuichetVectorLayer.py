# -*- coding: utf-8 -*-
"""
Created on 23 oct. 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse, NGremeaux
"""

import random
import hashlib
import os

from PyQt5.QtGui import QColor
from qgis.core import QgsVectorLayer, QgsProject, QgsEditorWidgetSetup, QgsSymbol, QgsFeatureRenderer, \
    QgsRuleBasedRenderer, QgsSingleSymbolRenderer, QgsLineSymbol, QgsFillSymbol, QgsMarkerSymbol, QgsUnitTypes, \
    QgsDefaultValue

from .MongoDBtoQGIS import MongoDBtoQGIS
from .SQLiteManager import SQLiteManager


class GuichetVectorLayer(QgsVectorLayer):
    # Les statistiques de comptage pour la couche
    stat = None

    databasename = ""

    # La liste des id/md5 par objet AVANT le travail de l'utilisateur
    #md5BeforeWorks = []

    # La liste des id/md5 par objet APRES le travail de l'utilisateur
    #md5AfterWorks = []

    # Les fichiers ou sont stockés les objets
    #repertoire = None
    fileBeforeWorks = None
    #fileAfterWorks = None

    # Correspondance champ/type
    correspondanceChampType = None

    sqliteManager = None

    srid = -1
    # Base historisée
    #idxFingerprint = -1                 ## index du champ gcms_fingerprint dans la couche
    #fingerprint = "gcms_fingerprint"    ## nom du champ gcms_fingerprint (présent sur les bases historisées)
    #listUpdatedFeaturesIds = None            ## liste des identifiants des objets créés/modifiés/supprimés

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
    #def __init__(self, uri, layerName, layerType, databasename, tableAttributes):
    def __init__(self, parameters):
        #super(GuichetVectorLayer, self).__init__(uri, layerName, layerType)
        super(GuichetVectorLayer, self).__init__(parameters['uri'], parameters['name'], parameters['genre'])
        #
        # Remplissage de idxFingerprint (index du champ gcms_fingerprint) pour les tables historisées
        #listFields = self.fields()
        #self.idxFingerprint = listFields.indexFromName(self.fingerprint)
        #self.listUpdatedFeaturesIds = []

        #self.connectSignals()
        #self.stat = Statistics(self.featureCount())
        #self.repertoire = projectDirectory
        #fileName = QgsProject.instance().fileName()
        #tmp = fileName.replace(".qgz", "")
        #nodeGroups = QgsProject.instance().layerTreeRoot().findGroups()
        #self.fileBeforeWorks = "{}{}{}_{}".format(tmp, nodeGroups[0].name(), layerName, "md5BeforeWorks.txt")
        #self.fileAfterWorks = "{}{}{}_{}".format(tmp, nodeGroups[0].name(), layerName, "md5AfterWorks.txt")
        self.databasename = parameters['databasename']
        self.sqliteManager = parameters['sqliteManager']
    '''
    Connexion des signaux pour les évènements survenus sur la carte
    '''
    def connectSignals(self):

        # Connexion des signaux permettant le traitement de gcms_fingerprint pour les tables historisées
        if self.idxFingerprint != -1:
            # Signaux pour la modification d'objets
            self.geometryChanged.connect(self.geometry_changed)
            self.attributeValueChanged.connect(self.attribute_value_changed)
            #self.featureAdded.connect(self.feature_added)
            #self.featureDeleted.connect(self.feature_deleted)

            # Signaux pour réinitialiser la liste des objets modifiés
            # self.afterCommitChanges.connect(self.clear_features_list)
            # self.afterRollBack.connect(self.clear_features_list)
            # self.editingStarted.connect(self.clear_features_list)
            # self.editingStopped.connect(self.clear_features_list)
            self.beforeCommitChanges.connect(self.before_commit_changes)

        self.attributeAdded.connect(self.attribute_added)
        self.attributeDeleted.connect(self.attribute_deleted)
        self.editingStopped.connect(self.editing_stopped)

    #def print_list(self):
    #    print(self.listUpdatedFeaturesIds)

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

        return feature.id(), cle

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
        print("Rechargement de la couche")
        self.reload()

    def attribute_value_changed(self, fid, idx, value):
        self.include_fingerprint(fid, idx)

    def geometry_changed(self, fid, geometry):
        self.include_fingerprint(fid)

    #def feature_deleted(self, fid):
     #   self.include_fingerprint(fid)

    def before_commit_changes(self):
        print("Before commit changes")

    '''
    Lors de toute modification sur un objet d'une table historisée (table contenant le champ gcms_fingerprint),
    on simule une modification du champ gcms_fingerprint pour que celui-ci soit inclus dans la transaction.
    Sinon, la transaction est refusée par l'espace collaboratif.
    '''
    def include_fingerprint(self, fid, idx = None):
        if idx is not None and (idx == self.idxFingerprint or self.idxFingerprint == -1):
            return

        #if fid in self.listUpdatedFeaturesIds:
        #    return

        feat = self.getFeature(fid)
        valFingerPrint = feat[self.fingerprint]
        self.changeAttributeValue(fid, self.idxFingerprint, valFingerPrint, valFingerPrint)

    '''
    Interdiction de supprimer un attribut sinon la synchronisation au serveur est perdue
    '''
    def attribute_deleted(self, idx):
        fields = self.fields()
        raise Exception("Impossible de supprimer l'attribut {} car la synchronisation au serveur sera perdue.".format(
            fields[idx].name()))

    '''
    Interdiction d'ajouter un attribut sinon la synchronisation au serveur est perdue
    '''
    def attribute_added(self, idx):
        fields = self.fields()
        raise Exception("Impossible d'ajouter l'attribut {} car la synchronisation au serveur sera perdue.".format(
            fields[idx].name()))

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

    def setModifyDefaultValue(self, listOfDefaultValues):
        fields = self.fields()
        for attribute, value in listOfDefaultValues.items():
            index = fields.indexOf(attribute)
            self.setDefaultValueDefinition(index, QgsDefaultValue(value))

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

    '''
        Définition de l'échelle minimum et maximum de la couche
        Source : https://geoservices.ign.fr/documentation/geoservices/wmts.html#taille-des-tuiles-en-pixels
    '''
    def setDisplayScale(self, min, max):
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
        self.setMinimumScale(scale[min])
        self.setMaximumScale(scale[max])
        self.setScaleBasedVisibility(True)
