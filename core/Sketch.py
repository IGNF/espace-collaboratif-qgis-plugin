# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
"""
from .Enum import Enum
import xml.etree.ElementTree as ET
from .ClientHelper import ClientHelper


class Sketch(object):
    """
    Classe représentant un croquis
    """
    '''
    Vide : pas de croquis
    Point : un point du croquis
    Ligne une polyligne du croquis
    Polygone: un polygone simple (sans trous et non multiple) du croquis.
    Texte : un champ texte du croquis
    Fleche : une flêche du croquis
    '''
    sketchType = Enum("Vide", "Point", "Ligne", "Polygone", "Texte", "Fleche")

    def __init__(self):
        # Type du croquis
        self.type = self.sketchType.Vide

        # Nom du croquis
        self.name = ""

        # La liste des attributs (clé, valeur)
        self.attributes = list()

        # La liste des points composants le croquis (coordonnées)
        self.points = list()

        self.coordinates = ""

    def addPoint(self, point):
        """
        Ajoute un point à la liste des points du croquis

        :param point:  un objet Point
        """
        self.points.append(point)

    def addAttribut(self, attribute):
        """Ajoute un attribut à la liste des attributs du croquis
        
        :param attribute : l'objet Attribut
        :type attribute: Attribute
        """
        self.attributes.append(attribute)

    def getPoint(self, i):
        """Recherche un point dans la liste de Points par sa position dans la liste
         
        :param i: la position du point à trouver
        :type i: int
        
        :return le point cherché
        :rtype Point
        """      
        return self.points[i]

    def longitude(self, i):
        """Retourne la longitude pour le point i
        
        :param i: l'index du point dans la liste
        :type i: int
        
        :return la longitude
        :rtype float
        """       
        return self.getPoint(i).longitude

    def latitude(self, i):
        """Retourne la latitude pour le point i
        
        :param i: l'index du point dans la liste
        :type i: int
        
        :return la latitude
        :rtype float
        """       
        return self.getPoint(i).latitude
                
    def firstCoord(self):
        """Retourne le premier point de la liste
        
        :return le premier point
        :rtype Point
        """
        if len(self.points) > 0:
            return self.points[0]
        else:
            return None

    def lastCoord(self):
        """Retourne le dernier point de la liste
        
        :return le dernier point
        :rtype Point
        """
        if len(self.points) > 0:
            return self.points[-1]
        else:
            return None

    def isClosed(self):
        """Contrôle si la géométrie est fermée
        rtype:boolean
        """
        return self.firstCoord() == self.lastCoord()

    def isValid(self):
        """Contrôle la validité de la géométrie
        """
        nPoints = len(self.points)
        if nPoints == 0 \
                or ((self.type == self.sketchType.Point or self.type == self.sketchType.Texte) and nPoints != 1)\
                or (self.type == self.sketchType.Polygone and not self.firstCoord().eq(self.lastCoord()))\
                or (self.type == self.sketchType.Vide and nPoints > 0):
            return False
        return True

    def encodeToXML(self, xmlDoc, ns='gml'):
        """Transforme les objets géométriques en xml 
        :param xmlDoc : le document xml représentant le croquis
        :param ns: le namespace
        
        :return le xml au format string
        """
        if self.type == self.sketchType.Vide:
            return xmlDoc
        
        objet = ET.Element('objet', {"type": self.type.__str__()})
        nom = ET.SubElement(objet, 'nom')
        nom.text = self.name
        
        # la geométrie
        geom = ET.SubElement(objet, 'geometrie')
        coord = ""
       
        for pt in self.points:
            coord += pt.longitude.__str__() + "," + pt.latitude.__str__() + " "
            
        coord = coord[:-1]
        ingeom = ''
        if self.type in [self.sketchType.Ligne, self.sketchType.Fleche]:
            ingeom = ET.SubElement(geom, ns+':LineString')
        elif self.type in [self.sketchType.Point, self.sketchType.Texte]:
            ingeom = ET.SubElement(geom, ns+':Point')
        elif self.type == self.sketchType.Polygone:
            pol = ET.SubElement(geom, ns+':Polygon')
            outer = ET.SubElement(pol, ns+':outerBoundaryIs')
            ingeom = ET.SubElement(outer, ns+':LinearRing')

        coordEl = ET.SubElement(ingeom, ns+':coordinates')
        coordEl.text = coord
        
        # les attributs
        xattributs = ET.SubElement(objet, 'attributs')
        for att in self.attributes:
            xatt = ET.SubElement(xattributs, 'attribut', {'name': ClientHelper.notNoneValue(att.nom)})
            xatt.text = ClientHelper.notNoneValue(att.valeur)
            
        xmlDoc.append(objet)
        return xmlDoc

    def getAttributsInStringFormat(self):
        """
        """
        satt = ""
        for att in self.attributes:
            # Anomalie Redmine #14757 : le SQL n'aime pas les %
            attributeName = att.name.replace('%', 'pourcent')
            attributeValue = att.value.replace('%', 'pourcent')
            satt += ClientHelper.notNoneValue(attributeName) + "='" + ClientHelper.notNoneValue(attributeValue) + "'|"
       
        if len(satt) > 0:
            satt = satt[:-1]
        
        return satt
            
    def getCoordinatesFromPoints(self):
        coord = ""
        for pt in self.points:
            coord += str(pt.longitude) + " " + str(pt.latitude) + ","
        return coord[:-1]    
