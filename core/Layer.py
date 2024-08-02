# -*- coding: utf-8 -*-
"""
Created on 25 MAY 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse
"""


class Layer(object):
    """
    Classe représentant les caractéristiques d'une couche
    """

    def __init__(self):
        # Attributs remplis avec gcms/api/communities/{community_id}/layers
        self.databaseId = None
        self.databasename = ''
        self.geoservice = {}
        self.id = None
        self.opacity = 1
        self.order = 0
        self.preferred_style = None
        self.role = 'visu'
        self.snapto = None
        self.table = 0
        self.type = 'feature-type'
        self.visibility = True
        # Attributs remplis avec gcms/api/databases/{database_id}/tables/{table_id}
        self.name = ''
        self.description = ""
        self.minzoom = 0
        self.maxzoom = 20
        self.isStandard = True
        self.tileZoomLevel = 0
        self.readOnly = None
        self.geometryName = ''
        self.geometryType = None
        self.wfs = ''
        self.wfsTransaction = ''
        self.attributes = []
        self.idName = None
        self.is3d = None
        self.style = {}
        self.srid = -1

    '''
        Pour l'item 'style', récupération de la symbologie d'une couche
    '''
    def getListOfValuesFromItemStyle(self):
        listOfValues = {}

        # La couche n'a pas de style défini, QGIS applique une symbologie par défaut
        if self.style is None:
            return listOfValues

        tmp = {'children': []}
        for stKey, stValues in self.style.items():
            if stKey == 'children':
                if type(stValues) is list and len(stValues) == 0:
                    continue
                else:
                    for dftvValue in stValues:
                        listOfValues[dftvValue['name']] = dftvValue
            else:
                tmp[stKey] = stValues
        listOfValues['default'] = tmp

        return listOfValues
