# -*- coding: utf-8 -*-
'''
Created on 29 sept. 2015

@author: AChang-Wailing
'''
import logging
from core.RipartLoggerCl import RipartLogger
import xml.etree.ElementTree as ET
from pyspatialite import dbapi2 as db
from qgis.core import QgsCoordinateReferenceSystem,QgsCoordinateTransform
from core.ClientHelper import ClientHelper
from RipartException import RipartException
import collections

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

    nom_Champ_IdRemarque = u"N°remarque"
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
    nom_Champ_LienBDuni = "Lien_object_BDUni"

    xml_UrlHost = "./Serveur/URLHost"
    xml_Login = "./Serveur/Login"
    xml_DateExtraction = "./Map/Date_extraction"
    xml_Pagination = "./Map/Pagination"
    xml_Themes = "./Map/Thèmes_préférés/Thème"
    xml_Zone_extraction = "./Map/Zone_extraction"
    xml_AfficherCroquis = "./Map/Afficher_Croquis"
    xml_AttributsCroquis = "./Map/Attributs_croquis"
    xml_BaliseNomCalque = "Calque_Nom"
    xml_BaliseChampCalque = "Calque_Champ"
    xml_Group = "./Map/Import_pour_groupe"

    url_Manuel = "C:\\Ripart\\Manuel d'utilisation de l'add-in RIPart pour ArcMap.pdf" 

    dateDefaut = "01/01/1900"
    longueurMaxChamp = 5000
    
    #epsgCrs= 2154
    epsgCrs = 4326
    
    
    #xmlroot=""
       
  
    logger=RipartLogger("RipartHelper").getRipartLogger()

    @staticmethod
    def load_urlhost(projectDir):
        urlhost=""
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            urlhost= xmlroot.find(RipartHelper.xml_UrlHost)     
            
        except Exception as e:
            RipartHelper.logger.error(str(e))
        
        return urlhost
    
    @staticmethod
    def load_login(projectDir):
        login=""
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            login= xmlroot.find(RipartHelper.xml_Login)     
            
        except Exception as e:
            RipartHelper.logger.error(str(e))
        
        return login
    
    @staticmethod
    def save_login(projectDir,login):
        try:
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            xlogin= xmlroot.find(RipartHelper.xml_Login)  
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
            calque= xmlroot.find(RipartHelper.xml_Zone_extraction)     
            
        except Exception as e:
            RipartHelper.logger.error(str(e))
        
        return  calque


    @staticmethod
    def load_ripartXmlTag(projectDir,tag):
        calque=""
        try:    
            tree= ET.parse(projectDir+"/"+RipartHelper.nom_Fichier_Parametres_Ripart)
            xmlroot =tree.getroot()
            calque= xmlroot.find(tag)     
            
        except Exception as e:
            RipartHelper.logger.error(str(e))
        
        return  calque
        
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
        RipartHelper.logger.debug("insertRemarques")
        
        cur = conn.cursor()
        
        try:
            RipartHelper.logger.debug("INSERT rem id:" + rem.id)
            ptx=rem.position.longitude
            pty= rem.position.latitude
            
            geom= " GeomFromText('POINT("+ ptx+" "+pty +")', 4326)"
            
            sql="INSERT INTO "+ RipartHelper.nom_Calque_Remarque + \
                " (NoRemarque, Auteur,Commune, Département, Département_id, Date_création, Date_MAJ," + \
                "Date_validation, Thèmes, Statut, Message, Réponses, URL, URL_privé, Document,Autorisation, geom) "+ \
                "VALUES (" + \
                 rem.id +", '" + \
                 rem.auteur.nom +"', '" + \
                 rem.getAttribut("commune") +"', '" + \
                 rem.getAttribut("departement","nom") +"', '" + \
                 rem.getAttribut("departement","id")+"', '" + \
                 rem.getAttribut("dateCreation")+"', '" + \
                 rem.getAttribut("dateMiseAJour")+"', '" + \
                 rem.getAttribut("dateValidation")+"', '" + \
                 rem.concatenateThemes()+"', '" + \
                 rem.statut.__str__()+"', '" + \
                 rem.getAttribut("commentaire") +"', '" + \
                 rem.concatenateReponse() +"', '" + \
                 rem.getAttribut("lien") +"', '" + \
                 rem.getAttribut("lienPrive") +"', '" + \
                 rem.getFirstDocument() +"', '" + \
                 rem.getAttribut("autorisation") + "', " + \
                 geom +")"
               
            RipartHelper.logger.debug("INSERT sql:" + sql)
            sql =ClientHelper.getEncodeType(sql)    
            
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
                        
                    values= "("+rem.id + ",'"+ \
                            ClientHelper.getValForDB(cr.nom ) + "', '" + \
                            ClientHelper.getValForDB(cr.getAttributsInStringFormat()) + "', %s)"
                            
                    sql += values
                          
                    sgeom= " GeomFromText('%s(%s)', 4326)" 
                    coord= cr.coordinates
                    if cr.type=="Point" :                        
                        geom= sgeom % ('POINT',coord)
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Point,geom)
                    elif cr.type =="Texte":
                        geom= sgeom % ('POINT',coord)
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Texte,geom)
                    elif cr.type=="Ligne":
                        geom= sgeom % ('LINESTRING',coord)
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Ligne,geom)
                    elif cr.type =="Fleche" :
                        geom= sgeom % ('LINESTRING',coord)
                        sql =sql % (RipartHelper.nom_Calque_Croquis_Ligne,geom)
                    elif cr.type=='Polygone':
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
        
        