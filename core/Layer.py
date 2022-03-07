# -*- coding: utf-8 -*-
"""
Created on 25 may 2020

version 4.0.1, 15/12/2020

@author: EPeyrouse
"""


class Layer(object):
    """
    Classe représentant les caractéristiques d'une couche appartenant au <GEOGROUPE>
    """
    # <TYPE> GeoPortail </TYPE>
    type = None
    # <NOM> ORTHOIMAGERY.ORTHOPHOTOS </NOM>
    nom = None
    # <DESCRIPTION> Photographies aériennes </DESCRIPTION>
    description = None
    # <MINZOOM> 0 </MINZOOM>
    minzoom = None
    # <MAXZOOM> 20 </MAXZOOM>
    maxzoom = None
    # <EXTENT> -180, -86, 180, 84 </EXTENT>
    extent = None
    # <ROLE> Droit utilisateur sur la couche </ROLE>
    role = None
    # <VISIBILITY> 1 </VISIBILITY>
    visibility = None
    # <OPACITY> 1 </OPACITY>
    opacity = None
    # <TILEZOOM>
    tilezoom = None
    # <URL>
    url = None
    # Extraction du nom de la base de données à partir de l'url
    databasename = None
    # SRID
    srid = None
    # <LAYER>
    layer_id = None

    def __init__(self):
        """
        Constructor
        """
        self.type = ""
        self.nom = ""
        self.description = ""
        self.minzoom = 0
        self.maxzoom = 20
        self.extent = None
        self.role = ""
        self.visibility = 1
        self.opacity = 1
        self.tilezoom = ""
        self.url = ""
        self.databasename = ""
        self.srid = -1
        self.layer_id = ""
        self.isStandard = True

    def GetAllInfo(self):
        infos = [self.type, self.nom, self.description, self.minzoom, self.maxzoom, self.extent, self.role,
                 self.visibility, self.opacity, self.tilezoom, self.url, self.databasename, self.layer_id,
                 self.isStandard]
        return infos
