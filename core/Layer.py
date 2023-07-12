# -*- coding: utf-8 -*-
"""
Created on 25 may 2020

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
        self.databaseName = ''
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
        self.isBduni = False
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
        # self.styles = []
        # les attributs suivants sont-ils utiles ?
        # self.extent = None
        # self.url = ""

