# -*- coding: utf-8 -*-
'''
Created on 29 sept. 2015

@author: AChang-Wailing
'''

from core.RipartLoggerCl import RipartLogger
import xml.etree.ElementTree as ET
from pyspatialite import dbapi2 as db

from qgis.core import QgsCoordinateReferenceSystem,QgsCoordinateTransform,QGis
from core.ClientHelper import ClientHelper
from RipartException import RipartException
import collections
from datetime import datetime
from PyQt4.QtGui import QMessageBox

from core.Croquis import Croquis
from core.Point import  Point

import errno
import shutil
import os, sys, subprocess

class RipartHelper(object):
    """"
    Classe contenant des utilitaires pour le plugin
    """
    
    ripart_files_dir="files"
    ripart_db = "ripart.sqlite"
    
    #fichier de configuration
    nom_Fichier_Parametres_Ripart = "Ripart.xml"
    
    #dossier des fichiers de style .qml
    qmlStylesDir="ripartStyles"          

    nom_Calque_Remarque = "Remarque_Ripart"
    nom_Calque_Croquis_Fleche = "Croquis_Ripart_Fleche"
    nom_Calque_Croquis_Texte = "Croquis_Ripart_Texte"
    nom_Calque_Croquis_Polygone = "Croquis_Ripart_Polygone"
    nom_Calque_Croquis_Ligne = "Croquis_Ripart_Ligne"
    nom_Calque_Croquis_Point = "Croquis_Ripart_Point"
   
    croquis_layers ={nom_Calque_Croquis_Polygone:'POLYGON',nom_Calque_Croquis_Ligne:'LINESTRING',
                    nom_Calque_Croquis_Fleche:'LINESTRING',nom_Calque_Croquis_Texte:'POINT',
                    nom_Calque_Croquis_Point:'POINT'}
     
    #liste des nom, car le dictionnaire ne préserve pas l'ordre des éléments
    croquis_layers_name=[nom_Calque_Croquis_Polygone,nom_Calque_Croquis_Ligne,
                    nom_Calque_Croquis_Fleche,nom_Calque_Croquis_Texte,
                    nom_Calque_Croquis_Point,nom_Calque_Remarque]

    calque_Remarque_Lyr = "Remarque_Ripart.lyr"

    """nom_Champ_IdRemarque = u"N°remarque"
    nom_Champ_Auteur = "Auteur"
    nom_Champ_Commune = "Commune"
    nom_Champ_Departement = u"Département"
    nom_Champ_IDDepartement = "Département_ID"
    nom_Champ_DateCreation = "Date_de_création"
    nom_Champ_DateMAJ = "Date_MAJ"
    nom_Champ_DateValidation = "Date_de_validation"
    nom_Champ_Themes = "Thèmes"
    nom_Champ_Statut = "Statut"
    nom_Champ_Message = "Message"
    nom_Champ_Reponse = "Réponses"
    nom_Champ_Url = "URL"
    nom_Champ_UrlPrive = "URL_privé"
    nom_Champ_Document = "Document"
    nom_Champ_Autorisation = "Autorisation"

    nom_Champ_LienRemarque = "Lien_remarque"
    nom_Champ_NomCroquis = "Nom"
    nom_Champ_Attributs = "Attributs_croquis"
    nom_Champ_LienBDuni = "Lien_object_BDUni"""

    xmlServeur="Serveur"
    xmlMap="Map"
  
    xml_UrlHost = "URLHost"
    xml_Login = "Login"
    xml_DateExtraction = "Date_extraction"
    xml_Pagination = "Pagination"
    xml_Themes = "Themes_pref"
    xml_Theme="Theme"
    xml_Zone_extraction = "Zone_extraction"
    xml_AfficherCroquis = "Afficher_Croquis"
    xml_AttributsCroquis = "Attributs_croquis"
    
    
    xml_BaliseNomCalque = "Calque_Nom"
    xml_BaliseChampCalque = "Calque_Champ"
    #xml_Group = "./Map/Import_pour_groupe"
    xml_Group ="Import_pour_groupe"
    xml_Map="./Map"
    
    xml_proxy="Proxy"

    defaultDate = "1900-01-01 00:00:00"
    defaultPagination=100
    longueurMaxChamp = 5000
    
    #Système de coordonnées de référence de Ripart
    epsgCrs = 4326
    
    logger=RipartLogger("RipartHelper").getRipartLogger()
    
    
    @staticmethod
    def getXPath(tagName,parentName):
        """Construction du xpath
        """
        xpath="./"+parentName+"/"+tagName
        return xpath
    

    @staticmethod
    def load_urlhost(projectDir):
        """Retourne l'url sauvegardé dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        urlhost=""
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            urlhost= xmlroot.find( RipartHelper.getXPath(RipartHelper.xml_UrlHost,"Serveur"))     
            if urlhost==None:
                urlhost=RipartHelper.addXmlElement(projectDir,"URLHost","Serveur")
                 
        except Exception as e:
            RipartHelper.logger.error(str(e))
    
        return urlhost
    
   
    
    @staticmethod
    def load_login(projectDir):
        """Retourne le login sauvegardé dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        login=""
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            login= xmlroot.find( RipartHelper.getXPath(RipartHelper.xml_Login,"Serveur"))     
            if login==None:
                login=RipartHelper.addXmlElement(projectDir,"Login","Serveur")
                
        except Exception as e:
            RipartHelper.logger.error(str(e))
    
        return login
    
    
    @staticmethod
    def save_login(projectDir,login):
        """Enregistre le login dans le fichier de configuration
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        
        :param login: le login
        :type login: string
        """
        try:
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            xlogin= xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_Login,"Serveur"))
            xlogin.text=login 
            
            tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
           
        except Exception as e:
            RipartHelper.logger.error(e.message)
            
       
    @staticmethod
    def load_proxy(projectDir):
        """Retourne le proxy sauvegardé dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        proxy=""
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            proxy= xmlroot.find( RipartHelper.getXPath(RipartHelper.xml_proxy,"Serveur"))     
            if proxy==None:
                proxy=RipartHelper.addXmlElement(projectDir,RipartHelper.xml_proxy,"Serveur")
                
        except Exception as e:
            RipartHelper.logger.error(str(e))
    
        return proxy
    
    
    @staticmethod
    def save_proxy(projectDir,proxy):
        """Enregistre le proxy dans le fichier de configuration
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        
        :param login: le login
        :type login: string
        """
        try:
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            xproxy= xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_proxy,"Serveur"))
            xproxy.text=proxy
            
            tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
           
        except Exception as e:
            RipartHelper.logger.error(e.message)
        
     
    @staticmethod
    def load_CalqueFiltrage(projectDir):
        """Retourne le nom du calque de filtrage sauvegardé dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        calque=""
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            calque= xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_Zone_extraction,"Map"))     
            
        except Exception as e:
            RipartHelper.logger.error(str(e))
        
        return  calque

 

    @staticmethod
    def load_ripartXmlTag(projectDir,tag,parent=None):
        """Recherche un élément (tag) dans le fichier xml.
        Si l'élément n'existe pas ,il est créé
        
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: string
        
        :param tag: xpath de l'élément cherché
        :type tag: string
        
        :param parent: xpath de l'élément parent
        :type parent: string
        
        :return l'élément xml recherché
        :rtype Element
        """
        node=None
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            node= xmlroot.find(RipartHelper.getXPath(tag,parent))     
            
            if node==None:
                node=RipartHelper.addXmlElement(projectDir, tag, parent)
            
        except Exception as e:
            RipartHelper.logger.error(str(e))
        
        return  node
    
    
    
    @staticmethod
    def addXmlElement(projectDir,elem,parentElem,value=None):
        """Ajoute un élément xml "elem", avec comme élémént paren "parentElem"
        
        :param elem: le nom de l'élément(tag) à ajouter
        :type elem: string
        
        :param parentElem: le nom de l'élément parent
        :type parentElem: string
        
        :return l'élément xml créé
        :rtype: Element
        """
        tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
        xmlroot =tree.getroot()
        if parentElem!="root":
            parentNode= xmlroot.find(parentElem)  
        else:
            parentNode=xmlroot  
        if parentNode==None:
            parentNode=RipartHelper.addXmlElement(projectDir, parentElem, "root")
            
        elementNode=ET.SubElement(parentNode,elem)
        
        if value!=None:
            elementNode.text=value
                    
        tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
        
        return elementNode
    
    
    @staticmethod
    def load_attCroquis(projectDir):
        """Retourne les attributs de croquis sauvegardés dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        attCroquis={}
        try:
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            nodes=xmlroot.findall(RipartHelper.getXPath(RipartHelper.xml_AttributsCroquis,"Map"))
            
            for cr in nodes:
                nomCalque=cr.find(RipartHelper.xml_BaliseNomCalque).text
                attCroquis[nomCalque]=[]
                fields=cr.iter(RipartHelper.xml_BaliseChampCalque)
                for f in fields:
                    attCroquis[nomCalque].append(f.text)
                
        except Exception as e:
            RipartHelper.logger.error(str(e))
            
        return attCroquis
    
    @staticmethod
    def load_preferredThemes(projectDir):
        """Retourne les thèmes sauvegardés dans le fichier de configuration xml
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        """
        prefThemes=[]
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            
            prefThs= xmlroot.findall(RipartHelper.getXPath(RipartHelper.xml_Themes+"/"+RipartHelper.xml_Theme,"Map"))

            for n in  prefThs:
                prefThemes.append(n.text)  
         
        except Exception as e:
            RipartHelper.logger.error(str(e))
        
        return  prefThemes
    
    
    @staticmethod
    def save_preferredThemes(projectDir,prefThemes):
        """Enregistre les thèmes dans le fichier de config
        
        :param projectDir: le chemin vers le répertoire du projet
        :type projectDir: string
        
        :param prefThemes: la liste de  thèmes
        :type prefThemes: list de Theme
        """
        #first load Themes_prefs tag (create the tag if the tag doesn't exist yet)
        themesNode= RipartHelper.load_ripartXmlTag(projectDir,RipartHelper.xml_Themes,"Map")
        RipartHelper.removeNode(projectDir, RipartHelper.xml_Theme,"Map/"+RipartHelper.xml_Themes )
        
        for th in prefThemes:
            RipartHelper.addXmlElement(projectDir,  RipartHelper.xml_Theme, "Map/"+RipartHelper.xml_Themes, th.groupe.nom)
            
    
    @staticmethod
    def addNode(projectDir,tag,value, parentTag=None):
        try:
            tree = ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot = tree.getroot()
            if parentTag == None:
                parentNode = xmlroot
            else:   
                parentNode = xmlroot.find(parentTag)
                
            newTag=ET.SubElement(parentNode, tag)
            newTag.text=value
               
            tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
            
        except Exception as e:
            RipartHelper.logger.error(e.message)
    
    @staticmethod
    def removeNode(projectDir,tag, parentTag=None):
        try:
            tree = ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot = tree.getroot()
            if parentTag == None:
                parentNode = xmlroot
            else:   
                parentNode = xmlroot.find(parentTag)
                
            for c in parentNode.findall(tag):
                parentNode.remove(c)
               
            tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
            
        except Exception as e:
            RipartHelper.logger.error(e.message)
    
    
    @staticmethod
    def setXmlTagValue(projectDir,tag,value,parent=None):
        """Donne une valeur à un tag du fichier de config
        """
        try:
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            node= xmlroot.find(RipartHelper.getXPath(tag, parent))  
            node.text=value
            
            tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
           
        except Exception as e:
            RipartHelper.logger.error(e.message)
            

            
    @staticmethod
    def setAttributsCroquis(projectDir,calqueName,values):
        try:
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            mapNode= xmlroot.find(RipartHelper.xml_Map)
            
            nodeAtributsCroquis= ET.SubElement(mapNode,'Attributs_croquis')
            nodeNom= ET.SubElement(nodeAtributsCroquis,'Calque_Nom')
            nodeNom.text=calqueName
            for val in values:
                field= ET.SubElement(nodeAtributsCroquis,'Calque_Champ')
                field.text=val
            
            tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
        except Exception as e:
            print e.message
        
    @staticmethod
    def removeAttCroquis(projectDir,):
        tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
        xmlroot =tree.getroot()
        maptag= xmlroot.find('Map')
        for c in maptag.findall('Attributs_croquis'):
            maptag.remove(c)
        tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
            
         
    @staticmethod    
    def createRemarqueTable(conn):   
        """Création de la table Remarque_Ripart
        """
        
        sql=u"CREATE TABLE Remarque_Ripart (" + \
            u"id INTEGER NOT NULL PRIMARY KEY," + \
            u"NoRemarque INTEGER,"  + \
            u"Auteur TEXT, " + \
            u"Commune TEXT, " + \
            u"Département TEXT, " + \
            u"Département_id  TEXT,"+ \
            u"Date_création TEXT,"+ \
            u"Date_MAJ TEXT,"+ \
            u"Date_validation TEXT,"+ \
            u"Thèmes TEXT ,"+ \
            u"Statut TEXT ,"+ \
            u"Message TEXT,"+ \
            u"Réponses TEXT,"+ \
            u"URL TEXT,"+ \
            u"URL_privé TEXT ,"+ \
            u"Document TEXT,"+ \
            u"Autorisation TEXT)"
        
        cur = conn.cursor()
        r=cur.execute(sql)
        
        # creating a POINT Geometry column
        sql = "SELECT AddGeometryColumn('Remarque_Ripart',"
        sql += "'geom', "+str(RipartHelper.epsgCrs)+", 'POINT', 'XY')"
        cur.execute(sql)
        
        cur.close()
        
    
        
  
    @staticmethod     
    def createCroquisTable(conn,table,geomType):
        """Création d'une table de croquis
        
        :param conn: la connexion à la base de données
        :type conn: 
        
        :param table: le nom de la table à créer
        :type table: string
        
        :param geomType: le type de la géométrie 
        :type: string
        """
        cur = conn.cursor()
        
        sql=u"CREATE TABLE "+table+" (" + \
            u"id INTEGER NOT NULL PRIMARY KEY," + \
            u"NoRemarque INTEGER,"  + \
            u"Nom TEXT ,"+ \
            u"Attributs_croquis,"+ \
            u"Lien_objet_BDUNI TEXT) " 
        
        cur.execute(sql)
        
        # creating a POINT Geometry column
        sql = "SELECT AddGeometryColumn('"+table+"',"
        sql += "'geom', "+str(RipartHelper.epsgCrs)+",'"+geomType+"', 'XY')"
        cur.execute(sql)
        
        cur.close()
        
        
    @staticmethod    
    def emptyTable(conn,table):
        """Vide le contenu de la table donnée en paramètre
        
        :param conn: la connexion à la base de données
        :type conn: 
        
        :param table: la table à vider
        :type: string
        """

        cur = conn.cursor()
        try:
            sql=u"DELETE FROM "+table
            
            cur.execute(sql)
            rowcount=cur.rowcount
            
            sql =u"SELECT count(*) FROM "+ table
            cur.execute(sql)
            rowcount=cur.rowcount
        finally: 
            cur.close()
        
    
    @staticmethod
    def insertRemarques(conn,rem):
        """Insertion d'une nouvelle remarque dans la table Remarque_Ripart
        
        @param conn: la connexion à la base de données
        @type conn: 
        
        @param rem: la remarque à ajouter
        @type rem: Reamarque  
        """
        RipartHelper.logger.debug("insertRemarques")
        
        cur = conn.cursor()
        
        try:
            RipartHelper.logger.debug("INSERT rem id:" + str(rem.id))
             
            ptx=rem.position.longitude
            pty= rem.position.latitude
            
            geom= " GeomFromText('POINT("+ str(ptx)+" "+str(pty) +")', 4326)"
            
            if type(rem.dateCreation)==datetime:
                rem.dateCreation=RipartHelper.formatDatetime(rem.dateCreation)
            if type(rem.dateMiseAJour)==datetime:
                rem.dateMiseAJour=RipartHelper.formatDatetime(rem.dateMiseAJour)
            if type(rem.dateValidation)==datetime:
                rem.dateValidation=RipartHelper.formatDatetime(rem.dateValidation)
            
            if rem.dateValidation==None: 
                rem.dateValidation=""
                
             
            sql=u"INSERT INTO "+ RipartHelper.nom_Calque_Remarque 
            sql+= u" (NoRemarque, Auteur,Commune, Département, Département_id, Date_création, Date_MAJ," 
            sql+= u"Date_validation, Thèmes, Statut, Message, Réponses, URL, URL_privé, Document,Autorisation, geom) "
            sql+= u"VALUES (" 
            sql+= str(rem.id) +", '" 
            sql+= ClientHelper.getEncodeType(ClientHelper.getValForDB(rem.auteur.nom) +"', '" )
            sql+= ClientHelper.getEncodeType(rem.getAttribut("commune") +"', '" )
            sql+= ClientHelper.getEncodeType(rem.getAttribut("departement","nom") +"', '" )
            sql+= ClientHelper.getEncodeType(rem.getAttribut("departement","id")+"', '" )
            sql+= rem.dateCreation+"', '" 
            sql+= rem.dateMiseAJour +"', '" 
            sql+= rem.dateValidation+"', '" 
            sql+= ClientHelper.getEncodeType(rem.concatenateThemes()+"', '") 
            sql+= ClientHelper.getEncodeType(rem.statut.__str__()+"', '" )
            sql+= ClientHelper.getEncodeType(rem.getAttribut("commentaire") +"', '")
            sql+= ClientHelper.getEncodeType(ClientHelper.getValForDB(rem.concatenateReponse()) +"', '" )
            sql+= ClientHelper.getEncodeType(rem.getAttribut("lien") +"', '" )
            sql+= ClientHelper.getEncodeType(rem.getAttribut("lienPrive") +"', '" )
            sql+= ClientHelper.getEncodeType(ClientHelper.getValForDB(rem.getFirstDocument()) +"', '" )
            sql+= ClientHelper.getEncodeType(rem.getAttribut("autorisation") + "', ") 
            sql+= ClientHelper.getEncodeType(geom +")")
               
            #RipartHelper.logger.debug("INSERT sql:" + sql)
           
            cur.execute(sql)
            rowcount=cur.rowcount
            if rowcount!=1:
                RipartHelper.logger.error("No row inserted:" + sql)
                           
            if len(rem.croquis) >0 :
                croquis= rem.croquis
                geom=None
             
                for cr in croquis:
                    sql="INSERT INTO %s (NoRemarque, Nom,Attributs_croquis,geom) VALUES "
                    if len(cr.points)==0:
                        return
                        
                    values= "("+str(rem.id) + ",'"+ \
                            ClientHelper.getValForDB(cr.nom ) + "', '" + \
                            ClientHelper.getValForDB(cr.getAttributsInStringFormat()) + "', %s)"
                            
                    sql += values
                          
                    sgeom= " GeomFromText('%s(%s)', 4326)" 
                    coord= cr.getCoordinatesFromPoints()

                    if str(cr.type)=="Point" :                        
                        geom= sgeom % ('POINT',coord)
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Point,geom)
                    elif str(cr.type) =="Texte":
                        geom= sgeom % ('POINT',coord)
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Texte,geom)
                    elif str(cr.type)=="Ligne":
                        geom= sgeom % ('LINESTRING',coord)
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Ligne,geom)
                    elif str(cr.type) =="Fleche" :
                        geom= sgeom % ('LINESTRING',coord)
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Ligne,geom)
                    elif str(cr.type)=='Polygone':
                        geom= sgeom % ('POLYGON(',coord+")")
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Polygone,geom)
                    cur.execute(sql) 
                
        
        except Exception as e:
            RipartHelper.logger.error(e.message)
            raise
        finally:
            cur.close()
    
    
        
    
    @staticmethod
    def isInGeometry(pt, geomLayer):
        """Si le point est dans la géométrie (définie par les objets d'une couche donnée)
        
        :param pt le point
        :type pt : geometry
        
        :param geomlayer: le calque
        :param geomLayer: QgsVectorlayer
        """
        
        layerCrs=  geomLayer.crs()
        destCrs= QgsCoordinateReferenceSystem(RipartHelper.epsgCrs, QgsCoordinateReferenceSystem.EpsgCrsId)
        xform= QgsCoordinateTransform(layerCrs, destCrs)
        
        featsPoly = geomLayer.getFeatures()
 
        isWithin=False
        
        for featPoly in featsPoly:
            #geomPoly = xform.transform(featPoly.geometry())
            geomPoly = featPoly.geometry()
            geomPoly.transform(xform)
            
            if pt.within(geomPoly):
                isWithin= True
            
        return isWithin            
    
  
    
    @staticmethod
    def getBboxFromLayer(filtreLay):
        """Retourne la bbox du calque donné en paramètre
        
        :param filtreLay: le calque
        :type filtreLay: QgsVectorlayer
        """
        filtreExtent= filtreLay.extent()
        
        filtCrs= filtreLay.crs()
        destCrs= QgsCoordinateReferenceSystem(RipartHelper.epsgCrs, QgsCoordinateReferenceSystem.EpsgCrsId)
        
        xform= QgsCoordinateTransform(filtCrs, destCrs)
        
        bbox= xform.transform(filtreExtent)
        
        return bbox
        
        
    @staticmethod
    def formatDate(sdate):
        """
        Transforme une date donnée au format dd/MM/yyyy %H:%M:%S en yyyy-MM-dd %H:%M:%S
        
        :param sdate la date à tranformer
        :type sdate: string
        
        :return date au format yyyy-MM-dd %H:%M:%S
        :rtype: string
        """
        try:
            if len(sdate.split("/"))>0:
                dt= datetime.strptime(sdate, '%d/%m/%Y %H:%M:%S')
                rdate= dt.strftime('%Y-%m-%d %H:%M:%S')
            elif len(sdate.split("-"))>0:
                rdate=sdate
        except Exception as e:
            rdate=RipartHelper.defaultDate
        return rdate
    
    
    @staticmethod
    def formatDatetime(dt):
        """Retourne la date au format '%Y-%m-%d %H:%M:%S'
        
        :param dt : la date
        :type dt: datetime
        """
        rdate=dt.strftime('%Y-%m-%d %H:%M:%S')
        return rdate
    
 
   
    @staticmethod   
    def showMessageBox( message):
        """Affiche une fen^tre avec le message donné
        
        :param message
        :type message: string
        """
        msgBox = QMessageBox()
        msgBox.setWindowTitle("IGN RIPart")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        ret = msgBox.exec_()
        
    
    @staticmethod         
    def copy(src, dest):
        """Copie un fichier ou un répertoire 
        
        :param src: le fichier ou répertoire source
        :type src: string
        
        :param destt : le fichier ou répertoire de destionation
        :type dest: string
        """
        try:
            if not os.path.exists(dest):
                shutil.copytree(src, dest)
        
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                if not os.path.exists(dest):
                    shutil.copy(src, dest)
            else:
                print('Directory not copied. Error: %s' % e)
                
                
    @staticmethod  
    def open_file(filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])