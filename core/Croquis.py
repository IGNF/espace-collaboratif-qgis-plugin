# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from Enum import Enum
from Point import Point
import xml.etree.ElementTree as ET


class Croquis(object):
    """
    Classe repésentant un croquis
    """
    
    '''
    Vide : pas de croquis
    Point : un point du croquis
    Ligne une polyligne du croquis
    Polygone: un polygone simple (sans trous et non multiple) du croquis.
    Texte : un champ texte du croquis
    Fleche : une flêche du croquis
    '''
    CroquisType = Enum( "Vide","Point","Ligne","Polygone","Texte","Fleche") 
    
    #Type du croquis
    type = CroquisType.Vide
    
    # Nom du croquis
    nom = None
    
    #La liste des attributs (clé,valeur)
    attributs = list()
    
    #La liste des points composants le croquis (coordonnées)
    points = list()
    

  

    def __init__(self, nom=None, typeCroquis=CroquisType.Vide, points=None):
        """
        Constructeur d'un croquis
        
        :param nom: string le nom du croquis
        :param typeCroquis: CroquisType le type du croquis
        :param points: une liste de points 
        """
        self.nom = nom
        
        self.type = typeCroquis
        
        if points is None:
            self.points=list()
        else:
            self.points= points


    def setType(self,typeCroquis):     
        """
        définit le type
        """
        self.type=typeCroquis
         
         
         
    def addPoint(self,point):
        """
        Ajoute un point à la liste des points du croquis

        :param point:  un objet Point
        """
        self.points.append(point)
        
    def addAttribut(self,attribut):
        """Ajoute un attribut à la liste des attributs du croquis
        
        :param attribut : l'objet Attribut
        :type attribut: Attribut
        """
        self.attributs.append(attribut)
        

    
    def getPoint(self,i):
        """Recherche un point dans la liste de Points par sa position dans la liste
         
        :param i: la position du point à trouver
        :type i: int
        
        :return le point cherché
        :rtype Point
        """      
        return self.points[i]


    def longitude(self,i):
        """Retourne la longitude pour le point i
        
        :param i: l'index du point dans la liste
        :type i: int
        
        :return la longitude
        :rtype float
        """       
        return self.getPoint(i).longitude
    
    
    
    def latitude(self,i):
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
        if len(self.points) >0 :
            return self.points[0]
        else:
            return None
    
    def lastCoord(self):
        """Retourne le dernier point de la liste
        
        :return le dernier point
        :rtype Point
        """
        if len(self.points) >0 :
            return self.points[-1]
        else:
            return None
        
        
    def isEmpty(self):
        """Contrôle si la liste de points est vide
         :return true si la liste est vide, false sinon
         :rtype boolean
         """
        return len(self.points)==0
    
    
    def isClosed(self):
        """Contrôle si la géométrie est fermée
        rtype:boolean
        """
        return self.firstCoord()==self.lastCoord()
                                                 
    def isOpenLine(self):
        """Contrôle si la ligne est ouverte
        :rtype boolean
        """      
        return   (self.type == self.CroquisType.Fleche or self.type == self.CroquisType.Ligne) and not self.isClosed()                                           
         
    
    def isValid(self):
        """Contrôle la validité de la géométrie
        """
        nPoints = len(self.points)
        if (nPoints==0):
            return False
        elif (self.type==self.CroquisType.Point or self.type == self.CroquisType.Texte) and nPoints!=1 :
            return False
        elif self.type ==self.CroquisType.Polygone and self.firstCoord() != self.lastCoord() :
            return False
        
        return True
    
    
    def encodeToXML(self,xmlDoc,ns='gml'):
        """Transforme les objets géométriques en xml 
        :param doc : le document xml représentant le croquis
        :param ns: le namespace
        
        :return le xml au format string
        """
        objet =ET.Element('objet',{"type": self.type.tostring()})    
        nom = ET.SubElement(objet,'nom')
        
        #la geométrie
        geom= ET.SubElement(objet,'geometrie')
        coord=""
       
        for pt in self.points:
            coord += pt.longitude.__str__()+ ","+ pt.latitude.__str__() + " "
        
        #if self.type==self.CroquisType.Ligne or self.type==self.CroquisType.Fleche:
        if self.type in [self.CroquisType.Ligne,self.CroquisType.Fleche]:
            ingeom=ET.SubElement(geom,ns+':LineString')
           
 
        #elif self.type==self.CroquisType.Point or self.type==self.CroquisType.Texte:
        elif self.typ in [self.CroquisType.Point,self.CroquisType.Texte]:
            ingeom=ET.SubElement(geom,ns+':Point')
    
        elif self.type == self.CroquisType.Polygone:
            pol=ET.SubElement(geom,ns+':Polygon')
            outer=ET.SubElement(pol,ns+':outerBoundaryIs')
            ingeom= ET.SubElement(pol,ns+':LinearRing')
      
        
        coordEl=ET.SubElement(ingeom,ns+':coordinates')
        coordEl.text=coord
        
        #les attributs
        xattributs= ET.SubElement(objet,'attributs')
        for att in self.attributs:
            xatt= ET.SubElement(xattributs,'attribut',{'name':att.nom})
            xatt.text = att.valeur
            
        xmlDoc.append(objet)
        
        return xmlDoc
        #print ET.tostring(objet)

if __name__ == "__main__":
    c= Croquis()
    
    pt= Point(2,3)
    
    print c.CroquisType.Point
    for each in c.CroquisType:
            print 'Day:', each

    c= Croquis("le croquis",Croquis.CroquisType.Point,[Point(1,20)])
    print c.nom
