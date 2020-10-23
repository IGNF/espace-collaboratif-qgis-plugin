# -*- coding: utf-8 -*-
"""
Created on 25 mai 2020

version 4.0.0

@author: EPeyrouse
"""


class Layer(object):
    """
    Classe représentant les caractéristiques d'une couche appartenant au <GEOGROUPE>
    """

    # <TYPE> GeoPortail </TYPE>
    type = ""
    # <NOM> ORTHOIMAGERY.ORTHOPHOTOS </NOM>
    nom = ""
    # <DESCRIPTION> Photographies aériennes </DESCRIPTION>
    description = ""
    # <MINZOOM> 0 </MINZOOM>
    minzoom = 0
    # <MAXZOOM> 20 </MAXZOOM>
    maxzoom = 20
    # <EXTENT> -180, -86, 180, 84 </EXTENT>
    extent = None
    # <ROLE> Droit utilisateur sur la couche </ROLE>
    role = ""
    # <VISIBILITY> 1 </VISIBILITY>
    visibility = 1
    # <OPACITY> 1 </OPACITY>
    opacity = 1
    # <TILEZOOM>
    tilezoom = ""
    # <URL>
    url = ""

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

    def GetAllInfo(self):
        infos = [self.type, self.nom, self.description, self.minzoom, self.maxzoom, self.extent, self.role,
                 self.visibility, self.opacity, self.tilezoom, self.url]
        return infos
