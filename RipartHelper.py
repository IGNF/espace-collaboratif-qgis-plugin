# -*- coding: utf-8 -*-
'''
Created on 29 sept. 2015

@author: AChang-Wailing
'''
import logging
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

class RipartHelper(object):
    """"
    Classe contenant des utilitaires pour le plugin
    """
    
    ripart_files_dir="files"
    ripart_db = "ripart.sqlite"
    nom_Fichier_Parametres_Ripart = "Ripart.xml"

    nom_Calque_Remarque = "Remarque_Ripart"
    nom_Calque_Croquis_Fleche = "Croquis_Ripart_Fleche"
    nom_Calque_Croquis_Texte = "Croquis_Ripart_Texte"
    nom_Calque_Croquis_Polygone = "Croquis_Ripart_Polygone"
    nom_Calque_Croquis_Ligne = "Croquis_Ripart_Ligne"
    nom_Calque_Croquis_Point = "Croquis_Ripart_Point"
   
    croquis_layers ={nom_Calque_Croquis_Polygone:'POLYGON',nom_Calque_Croquis_Ligne:'LINESTRING',
                    nom_Calque_Croquis_Fleche:'LINESTRING',nom_Calque_Croquis_Texte:'POINT',
                    nom_Calque_Croquis_Point:'POINT'}
    #croquis_layers =collections.OrderedDict([(key, c[key]) for key in c])
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
    """xml_UrlHost = "./Serveur/URLHost"
    xml_Login = "./Serveur/Login"
    xml_DateExtraction = "./Map/Date_extraction"
    xml_Pagination = "./Map/Pagination"
    xml_Themes = "./Map/Thèmes_préférés/Thème"
    xml_Zone_extraction = "./Map/Zone_extraction"
    xml_AfficherCroquis = "./Map/Afficher_Croquis"
    xml_AttributsCroquis = "./Map/Attributs_croquis"
    """
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

    url_Manuel = "C:\\Ripart\\Manuel d'utilisation de l'add-in RIPart pour ArcMap.pdf" 

    defaultDate = "1900-01-01 00:00:00"
    defaultPagination=100
    longueurMaxChamp = 5000
    
    #Système de coordonnées de référence de Ripart
    epsgCrs = 4326
    
    
    #xmlroot=""
       
  
    logger=RipartLogger("RipartHelper").getRipartLogger()
    
    @staticmethod
    def getXPath(tagName,parentName):
        xpath="./"+parentName+"/"+tagName
        return xpath
    

    @staticmethod
    def load_urlhost(projectDir):
        urlhost=""
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            urlhost= xmlroot.find( RipartHelper.getXPath(RipartHelper.xml_UrlHost,"Serveur"))     
            if urlhost==None:
                urlhost=RipartHelper.addXmlElement(projectDir,"URLHost","Serveur")
                #urlhost=""
                
        except Exception as e:
            RipartHelper.logger.error(str(e))
           
        
        return urlhost
    
   
    
    @staticmethod
    def load_login(projectDir):
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
        try:
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            xlogin= xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_Login,"Serveur"))
            xlogin.text=login 
            
            tree.write(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart,encoding="utf-8")
           
        except Exception as e:
            RipartHelper.logger.error(e.message)
        
     
    @staticmethod
    def load_CalqueFiltrage(projectDir):
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
        """
        :param projectDir: le répertoire dans lequel est enregistré le projet QGIS
        :type projectDir: string

        """
        prefThemes=[]
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            #prefThsTag= xmlroot.find(RipartHelper.getXPath(RipartHelper.xml_Themes,"Map"))  
            
            
            prefThs= xmlroot.findall(RipartHelper.getXPath(RipartHelper.xml_Themes+"/"+RipartHelper.xml_Theme,"Map"))
             
            #ths=prefThsTag.findall(RipartHelper.xml_Theme)
       
            for n in  prefThs:
                prefThemes.append(n.text)  
                
            """for th in prefThsTag:
                ths=prefThsTag.findall(RipartHelper.xml_Theme)
                
                if ths!=None:
                    for n in ths:
                        prefThemes.append(n.text)
            """   
            
        except Exception as e:
            RipartHelper.logger.error(str(e))
        
        return  prefThemes
    
    @staticmethod
    def save_preferredThemes(projectDir,prefThemes):
        """
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
        """Création de la table Remarque_Ripart"""
        
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
        """
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
               
            RipartHelper.logger.debug("INSERT sql:" + sql)
            #sql =ClientHelper.getEncodeType(sql)    
            
            cur.execute(sql)
            rowcount=cur.rowcount
            if rowcount!=1:
                print "error"
                           
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
        
        :param pt 
        :type pt : geometry
        
        :param
        :param geomLayer layer
        """
        #pt =QgsGeometry.fromWkt("POINT(3 4)")
        
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
    
    #@staticmethod
    #def transformGeomToRipartCrs(geom, sourceCrs):
        
        
    
    
    @staticmethod
    def getBboxFromLayer(filtreLay):
        
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
        rdate=dt.strftime('%Y-%m-%d %H:%M:%S')
        return rdate
    
    
    @staticmethod
    def creerPointRemarqueRipart(listCroquis):
        """
        Calcule le point d'application pour une nouvelle remarque Ripart à partir des croquis associées:
        On calcule le centroïde de chaque croquis de la liste donnée,
        puis le barycentre de l'ensemble de ces centroïdes calculés et 
        enfin on retient le centroïde le plus proche du barycentre calculé (pour que la remarque soit proche d'un croquis)
        """
        position=Point()
        cntCr= len(listCroquis)
        
        if cntCr==0:
            return None
        elif cntCr==1:
            if listCroquis[0].type== listCroquis[0].CroquisType.Point :
                return listCroquis[0].firstCoord()
            else:
                position= RipartHelper.Tra
        
            
    @staticmethod
    def getCroquisCentroid(croquis):
        """Calcule le centroïde d'un objet croquis Ripart.   
        
        :param croquis : le croquis pour lequel on calcule le centroïde
        :type croquis : core.Croquis
        
        :return le centroide 
        :rtype Point
        """  
        #le croquis n'est pas défini     
        if croquis.type==croquis.CroquisType.Vide or len(croquis.points)==0:
            return None
        
        #le croquis se résume à un point
        if croquis.type==croquis.CroquisType.Point :
            return croquis.firstCoord()
        
        #crée une table spatialite 
        #self.createTempCroquisTable(croquis)
        
        #RipartHelper.centroid(croquis.points)
        
  
    """@staticmethod
    def getMapCrs(sourceCrs):
        source_crs=QgsCoordinateReferenceSystem(RipartHelper.epsgCrs)
                    
        mapCrs=self.context.mapCan.mapRenderer().destinationCrs().authid()
        dest_crs=QgsCoordinateReferenceSystem(mapCrs)
                    
        transform = QgsCoordinateTransform(source_crs, dest_crs)
        new_box = transform.transformBoundingBox(box)
    """
    
    
    """@staticmethod     
    def createTempCroquisTable(croquis):
       
        dbName = self.projectFileName +"_RIPART"
        self.dbPath = self.projectDir+"/"+dbName+".sqlite"
        cur = conn.cursor()
        
        sql=u"CREATE TABLE "+"tmpTable"+" (" + \
            u"id INTEGER NOT NULL PRIMARY KEY)"  
        cur.execute(sql)
        
        # creating a POINT Geometry column
        sql = "SELECT AddGeometryColumn('"+table+"',"
        sql += "'geom', "+str(RipartHelper.epsgCrs)+",'"+geomType+"', 'XY')"
        cur.execute(sql)
        
        cur.close()
   """
    @staticmethod   
    def showMessageBox( message):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("IGN RIPart")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(message)
        ret = msgBox.exec_()
        
        