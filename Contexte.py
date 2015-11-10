# -*- coding: utf-8 -*-
'''
Created on 29 sept. 2015

@author: AChang-Wailing
'''
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QMessageBox
from qgis.core import *
from qgis.core import QgsCoordinateReferenceSystem, QgsMessageLog, QgsFeatureRequest,QgsCoordinateTransform,QgsGeometry
from RipartException import RipartException

import os.path
import shutil
from  RipartHelper import  RipartHelper

from core.RipartLoggerCl import RipartLogger

import ntpath
from core.Profil import Profil

# importing pyspatialite
from pyspatialite import dbapi2 as db

from qgis._core import QgsDataSourceURI,QgsVectorLayer, QgsMapLayerRegistry,QGis

from FormConnexion_dialog import FormConnexionDialog
from FormInfo import FormInfo
from core.Client import Client
from core.ClientHelper import ClientHelper
from core.Attribut import Attribut
from core.Point import Point
from core.Croquis import Croquis

import math

class Contexte(object):
    """
    Contexte et initialisation  
    """
    #instance du Contexte 
    instance =None
    
    #identifiants de connexion
    login=""
    pwd=""
    urlHostRipart=""    
    profil=None
    
    #client pour le service RIPart
    client=None
    
    #fenêtre de connexion
    loginWindow=None
 
    #le répertoire du projet qgis
    projectDir= ""    
    #le nom du fichier (projet qgis)
    projectFileName=""
    
    #chemin vers la base de donnée sqlite
    dbPath=""
    
    #répertoire du plugin
    plugin_path = os.path.dirname(os.path.realpath(__file__))
    
    #fichier xml de configuration
    ripartXmlFile=""
    
    #objets QGis
    QObject= None
    QgsProject=None
    iface=None
    
    #map canvas,la carte courante
    mapCan = None
    
    #Le système géodésique employé par le service Ripart (WGS84; EPSG:2154)
    spatialRef= None
      
    #connexion à la base de données
    conn=None
    
    #le logger
    logger=None
    
    #progressMessageBar=None
    progress=None
    

    def __init__(self, QObject,QgsProject):
        '''
        Constructor
        ''' 
        self.QObject=QObject
        self.QgsProject= QgsProject
        self.mapCan = QObject.iface.mapCanvas()
        
        self.iface= QObject.iface
        
        self.login=""
        self.pwd=""
        self.urlHostRipart=""
        
        self.logger=RipartLogger("Contexte").getRipartLogger()
  
        self.spatialRef = QgsCoordinateReferenceSystem( RipartHelper.epsgCrs, QgsCoordinateReferenceSystem.EpsgCrsId)
         
        try:
            #set du répertoire et fichier du projet qgis
            self.setProjectParams(QgsProject)
           
            #contrôle l'existence du fichier de configuration
            self.checkConfigFile()      
            
            self.getOrCreateDatabase()
      
        except RipartException as e:
            self.logger.error("init contexte:" + e.message)
            raise

    
    @staticmethod    
    def getInstance(QObject=None,QgsProject=None):
        """Retourne l'instance du Contexte
        """
        if not Contexte.instance:
            try:
                Contexte.instance= Contexte(QObject,QgsProject)
                Contexte.instance.logger.debug("instance de contexte créée")
            except RipartException as e:
                Contexte.instance=None
                #raise e
            
        elif  (Contexte.instance.projectDir!= QgsProject.instance().homePath() or
              Contexte.instance.projectFileName+".qgs"!=ntpath.basename(QgsProject.instance().fileName())) :
            Contexte.instance = Contexte(QObject,QgsProject)
            Contexte.instance.logger.debug("nouvelle instance de contexte créée")

        return Contexte.instance
    
    
    def setProjectParams(self,QgsProject):
        """set des paramètres du projet
        """
        self.projectDir=QgsProject.instance().homePath()
        if self.projectDir =="":   
            """self.iface.messageBar().pushMessage("Attention",
                                                 u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser l'extension RIPart",
                                                  level=1, duration =10)
            """
            RipartHelper.showMessageBox(u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser l'extension RIPart")
            raise RipartException(u"Projet QGIS non enregistré") 
    
        fname=ntpath.basename(QgsProject.instance().fileName())
        
        self.projectFileName= fname[:fname.find(".")]
        
    
    
    def checkConfigFile(self):
        """Contrôle de l'existence du fichier de configuration
        """
        ripartxml=self.projectDir+"\\"+ RipartHelper.nom_Fichier_Parametres_Ripart
        if not os.path.isfile(ripartxml) :
            try:
                shutil.copy(self.plugin_path+"\\"+RipartHelper.ripart_files_dir+"\\"+ RipartHelper.nom_Fichier_Parametres_Ripart,
                             ripartxml)
                self.logger.debug("copy ripart.xml" )
            except Exception as e:
                self.logger.error("no ripart.xml found in plugin directory" + e.message)
                raise Exception("Le fichier de configuration "+ RipartHelper.nom_Fichier_Parametres_Ripart + " n'a pqs été trouvé.")
           
    
    
    
    def setConnexionRipartParam(self):
        """Set des informations de connexion (login + url)
        """
        self.logger.debug("setConnexionRipart")
        ret=""
        if len(self.projectFileName)==0:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("IGN RIPart")
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText(u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser l'extension RIPart")
            ret = msgBox.exec_()
        else:
            self.urlHostRipart = RipartHelper.load_urlhost(self.projectDir).text
            self.login = RipartHelper.load_login(self.projectDir).text
        
        return ret
    
     
     
     
    def getConnexionRipart(self,newLogin=False):
        self.logger.debug("GetConnexionRipart ")
        
        result= -1;
        
        try:
            self.urlHostRipart=RipartHelper.load_ripartXmlTag(self.projectDir, RipartHelper.xml_UrlHost,"Serveur").text
            self.logger.debug("this.URLHostRipart " + self.urlHostRipart)
        except Exception as e:
            self.logger.error("URLHOST inexistant dans fichier configuration")
            RipartHelper.showMessageBox( u"L'url du serveur doit être renseignée dans la configuration avant de pouvoir se connecter.\n(Aide>Configurer le plugin RIPart>Adresse de connexion ...)" )
            return
 
        
        self.loginWindow = FormConnexionDialog()
        
        loginXmlNode=RipartHelper.load_ripartXmlTag(self.projectDir,RipartHelper.xml_Login,"Serveur")
        if loginXmlNode==None:
            self.login=""
        else:
            self.login = RipartHelper.load_ripartXmlTag(self.projectDir,RipartHelper.xml_Login,"Serveur").text
        
        if (self.login =="" or self.pwd=="" or newLogin):
            self.loginWindow.setLogin(self.login)
            self.loginWindow.exec_()

            while (result<0):      
                if self.loginWindow.cancel:
                    print "rejected"
                    self.loginWindow = None
                    result=0
                elif self.loginWindow.connect :
                    print "connect"
                    self.login = self.loginWindow.getLogin()
                    self.pwd=self.loginWindow.getPwd()
                    
                    try: 
                        client = Client(self.urlHostRipart, self.login, self.pwd)
                        profil = client.getProfil()
                        
                        if profil != None :
                            self.profil= profil
                            self.saveLogin(self.login)
                          
                            dlgInfo=FormInfo()
                            dlgInfo.textInfo.setText(u"<b>Connexion réussie au service RIPart.</b>")
                            dlgInfo.textInfo.append("<br/>Serveur : "+ self.urlHostRipart)
                            dlgInfo.textInfo.append("Login : "+  self.login)
                            dlgInfo.textInfo.append("Profil: "+ profil.titre)
                            dlgInfo.textInfo.append("Zone : "+ profil.zone.__str__())
    
                            dlgInfo.exec_()
                            
                            if dlgInfo.Accepted:
                                self.client=client
                                result= 1
                    except Exception as e:
                        result=-1
                        self.pwd=""
                        self.logger.error(e.message)         
                        self.loginWindow.setErreur(ClientHelper.getEncodeType(e.message))
                        self.loginWindow.exec_()
                        
        else: 
            try: 
                client = Client(self.urlHostRipart, self.login, self.pwd)   
                result=1
                self.client=client
            except RipartException as e:
                print e.message
                
        return result
    
    

    def saveLogin(self,login):
        self.login=login
        RipartHelper.save_login( self.projectDir, login)
    
   
    def getOrCreateDatabase(self):
        """
        """
        dbName = self.projectFileName +"_RIPART"
        self.dbPath = self.projectDir+"/"+dbName+".sqlite"
        
        createDb=False
            
        if not os.path.isfile(self.dbPath) :
            createDb=True
            try:
                shutil.copy(self.plugin_path+"\\"+RipartHelper.ripart_files_dir+"\\"+ RipartHelper.ripart_db,
                             self.dbPath)
                self.logger.debug("copy ripart.sqlite" )
            except Exception as e:
                self.logger.error("no ripart.sqlite found in plugin directory" + e.message)
                raise e
        try:    
            self.conn= db.connect(self.dbPath)
    
            # creating a Cursor
            cur = self.conn.cursor()
           
            sql="SELECT name FROM sqlite_master WHERE type='table' AND name='Remarque_Ripart'"  
            cur.execute(sql)       
            if cur.fetchone() ==None:
                #create layer Remarque_Ripart
                RipartHelper.createRemarqueTable(self.conn)
            
            for lay in RipartHelper.croquis_layers:  
                sql="SELECT name FROM sqlite_master WHERE type='table' AND name='"+lay+"'"
                cur.execute(sql)       
                if cur.fetchone() ==None:
                    #create layer 
                    RipartHelper.createCroquisTable(self.conn,lay,RipartHelper.croquis_layers[lay])
                    
        except RipartException as e:
            self.logger.error(e.message)
            raise
        finally:
            cur.close()
            self.conn.close()
        
      
      
      
    def addRipartLayersToMap(self):
        """Add ripart layers to the current map 
        """
        
        uri =QgsDataSourceURI()
        uri.setDatabase(self.projectFileName +"_RIPART.sqlite")
        
        maplayers=self.getAllMapLayers()
        
        #ripartLayers= RipartHelper.croquis_layers
        #ripartLayers[RipartHelper.nom_Calque_Remarque]="POINT"
          
        root = self.QgsProject.instance().layerTreeRoot()
        
        for table in RipartHelper.croquis_layers_name: 
            if table not in maplayers:
                uri.setDataSource('',  table, 'geom')
                uri.setSrid('4326')
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite') 
                vlayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                QgsMapLayerRegistry.instance().addMapLayer(vlayer,False)
                                
                root.insertLayer(0,vlayer)
        
        self.mapCan.refresh()
        
           
           
            
    """def getCheckedMapLayers(self):
        '''Return the list of layer names which are loaded in the map (and checked)'''
        
        layers = self.mapCan.layers()
        
        layerNames=[]
        maplayers={}
        for l in layers:
            layerNames.append(l.name())
            maplayers[l.name()]= l.id()
        
        return maplayers
        """
    
    def getAllMapLayers(self):
        """Return the list of layer names which are loaded in the map"""
        
        layers = QgsMapLayerRegistry.instance().mapLayers()

        layerNames=[]
        maplayers={}
        for key in layers:
            l=layers[key]
            layerNames.append(l.name())
            maplayers[l.name()]= l.id()
        
        return maplayers
    
    
    """def getMapPolygonLayers(self):
       '''Retourne les calques qui sont de type polygon ou multipolygon
       '''
        layers = self.mapCan.layers()
        polylayers={}
        
        for l in layers:
            if l.wkbType()==QGis.WKBPolygon or l.wkbType()==QGis.WKBMultiPolygon:
                polylayers[l.id()]=l.name()
                
        return polylayers
    """
    
    def getMapPolygonLayers(self):
        """Retourne les calques qui sont de type polygon ou multipolygon
        """
        layers = QgsMapLayerRegistry.instance().mapLayers()
        
        polylayers={}
        
        for key in layers:
            l=layers[key]
            if l.wkbType()==QGis.WKBPolygon or l.wkbType()==QGis.WKBMultiPolygon:
                polylayers[l.id()]=l.name()
                
        return polylayers
    
    
    
    """def getLayerByName(self,layName):
        layers = self.mapCan.layers()
   
        for l in layers:
            if l.name() == layName :
                return l
        
        return None
    """
    
    def getLayerByName(self,layName):
        mapByName= QgsMapLayerRegistry.instance().mapLayersByName(layName)
        if len(mapByName) >0:
            return mapByName[0]
        else:
            return None
        #return QgsMapLayerRegistry.instance().mapLayersByName(layName)[0]
    
    def emptyAllRipartLayers(self):
        """Supprime toutes les remarques vide les tables de la base ripart.sqlite 
        """
        ripartLayers= RipartHelper.croquis_layers
        ripartLayers[RipartHelper.nom_Calque_Remarque]="POINT"
              
        try:
        
            self.conn= db.connect(self.dbPath)
            
            for table in ripartLayers:
                RipartHelper.emptyTable(self.conn, table)
                
            self.conn.commit()    
        except RipartException as e:
            self.logger.error(e.message)
            raise
        finally:
            self.conn.close()
        
        self.refresh_layers()
        
        
        
    def refresh_layers(self):
        """
        """
        for layer in self.mapCan.layers():
            layer.triggerRepaint()


    def addRemarques(self,rems,importer):
        """
        """
        try:
            self.conn= db.connect(self.dbPath)

            for remId in rems:
                RipartHelper.insertRemarques(self.conn, rems[remId])
                
                #self.progress.setValue(i + 1)
                #i+=1
                importer.progressVal+=1
                importer.progress.setValue(importer.progressVal)
       
            self.conn.commit()   
           
        except Exception as e:
            self.logger.error(e.message)
            raise
        finally:
            self.conn.close()
     
    def addRemarques2(self,remId):
        """
        """
        try:
            self.conn= db.connect(self.dbPath)
    
            i=1
            
            RipartHelper.insertRemarques(self.conn, rems[remId])
            self.conn.commit()   
           
        except Exception as e:
            self.logger.error(e.message)
            raise
        finally:
            self.conn.close() 
     
    def updateRemarqueInSqlite(self,rem):
        """Met à jour une remarque (après l'ajout d'une réponse 
        
        :param rem : la remarque à mettre à jour
        :type rem: Remarque
        """
        try:
            self.conn= db.connect(self.dbPath)
            
            sql ="UPDATE "+ RipartHelper.nom_Calque_Remarque+" SET " + \
                " Date_MAJ= '" + rem.getAttribut("dateMiseAJour") +"'," + \
                " Date_validation= '" + rem.getAttribut("dateValidation") +"'," + \
                " Réponses= '" + ClientHelper.getValForDB(rem.concatenateReponse()) +"' "\
                " WHERE NoRemarque = " + str(rem.id)
            
            cur= self.conn.cursor()
            cur.execute(sql)
            
            self.conn.commit()

        except Exception as e :
            self.logger.error(e.message)
            raise
        finally:
            cur.close()
            self.conn.close()
        
   
    
    def countRemarqueByStatut(self,statut):  
        remLay=self.getLayerByName(RipartHelper.nom_Calque_Remarque)
        expression='"Statut" = \''+ statut +'\''
        filtFeatures=remLay.getFeatures(QgsFeatureRequest().setFilterExpression( expression ))
        return len(list(filtFeatures))
    
    #############Création nouvelle remarque ###########
    
    def hasMapSelectedFeatures(self):
        mapLayers = self.mapCan.layers()
        for l in mapLayers:
            if len(l.selectedFeatures())>0:
                return True        
        return False    
    
    """def getMapSelectedFeaturesCount(self):
        cnt=0
        mapLayers = self.mapCan.layers()
        for l in mapLayers:
            cnt+=len(l.selectedFeatures())
                     
        return cnt 
    """
    
    def makeCroquisFromSelection(self):
        """Transforme en croquis Ripart les object sélectionnés dans la carte en cours.
        Le système de référence spatial doit être celui du service Ripart(i.e. 4326), donc il faut transformer les
        coordonnées si la carte est dans un autre système de réf.
        """
        #dictionnaire : key: nom calque, value: liste des attributs 
        attCroquis=RipartHelper.load_attCroquis(self.projectDir)
        
        #Recherche tous les features sélectionnés sur la carte (pour les transformer en croquis)
        listCroquis=[]
        mapLayers = self.mapCan.layers()
        for l in mapLayers:
 
            for f in l.selectedFeatures():
                fattributes= f.attributes()
             
                ###CENTROID ??? 
                """centroid= f.geometry().centroid()
                centroidPt=centroid.asPoint()
                
                destCrs=QgsCoordinateReferenceSystem(RipartHelper.epsgCrs)
                transformer = QgsCoordinateTransform(l.crs(), destCrs)
                centroidPt=transformer.transform(centroidPt)
                """
                ######### 
                croquiss=[]
                ftype= f.geometry().wkbType()
                geom= f.geometry()
                #if geom.isMultipart():
                #explode to single parts
                if ftype == QGis.WKBMultiPolygon:
                    for poly in geom.asMultiPolygon():
                        croquiss.append(self.makeCroquis(QgsGeometry.fromPolygon(poly),QGis.WKBPolygon,l.crs(),f[0]))
                        
                elif ftype== QGis.WKBMultiLineString:
                    for line in geom.asMultiPolyline():
                        croquiss.append(self.makeCroquis(QgsGeometry.fromPolyline(line),QGis.WKBLineString,l.crs(),f[0]))
                        
                elif ftype== QGis.WKBMultiPoint:
                    for pt in geom.asMultiPoint():
                        croquiss.append(self.makeCroquis(QgsGeometry.fromPoint(pt),QGis.WKBPoint,l.crs(),f[0]))
               
                else :    
                    #croquisTemp=(self.makeCroquis(geom,ftype,l.crs(),f[0]))
                    croquiss.append(self.makeCroquis(geom,ftype,l.crs(),f[0]))
                
                if len(croquiss)==0:
                    continue
                
                for croquisTemp in croquiss:
                    if l.name() in attCroquis:
                        for att in attCroquis[l.name()]:
                            idx= l.fieldNameIndex(att)
                            attribut= Attribut(att,f.attributes()[idx])
                            croquisTemp.addAttribut(attribut)
                        
                    listCroquis.append(croquisTemp)
    
        return listCroquis
    
    
    def makeCroquis(self, geom, ftype, layerCrs,fId):
        """Génère un croquis Ripart à partir d'une géométrie
        Les coordonnées des points du croquis doivent être transformées dans le crs de Ripart (4326)
        
        :param geom: la géométrie à transformer en croquis
        :type geom: QgsGeometry
        
        :param ftype: le type de l'objet géométrique
        :param type ftype: QGis.WkbType
        
        :param layerCrs: le syst de coordonnées de référence du calque dont provient le feature
        :type layerCrs: QgsCoordinateReferenceSystem
        
        :param fId: l'id de l'objet géométrique (valeur du premier attribut du feature)
        :type fId: int
        
        :return le croquis créé 
        :rtype Croquis ou None s'il y a eu une erreur
        """
        croquisAndCentroids=[]
        
        #croquiss=[]
        
        newCroquis= Croquis()
        geomPoints=[]
        
        centroid=Point()
        
        try:
            destCrs=QgsCoordinateReferenceSystem(RipartHelper.epsgCrs)
            
            transformer = QgsCoordinateTransform(layerCrs, destCrs)
            #wgsGeom=transformer.transform(geom)
            
            #if geom.isMultipart():
                #explode to single parts
                
            if ftype == QGis.WKBMultiPolygon:
                #for poly in geom.asMultiPolygon():
                    #croquiss.append(self.makeCroquis(poly,ftype,layerCrs,fId))
                pass
            elif ftype==QGis.WKBPolygon:
                geomPoints=geom.asPolygon()
                if len(geomPoints)>0:
                    geomPoints=geomPoints[0]      #les points du polygone
                else: 
                    self.logger.debug(u"geomPoints problem " + str(fId))        
                newCroquis.type=newCroquis.CroquisType.Polygone
                
            elif ftype==QGis.WKBMultiLineString :
                geomPoints = geom.asMultiPolyline()
                
            elif ftype==QGis.WKBLineString:
                geomPoints = geom.asPolyline()
                newCroquis.type=newCroquis.CroquisType.Ligne
            
            elif ftype==QGis.WKBMultiPoint:
                geomPoints=geom.asMultiPoint()
                
            elif ftype==QGis.WKBPoint:
                geomPoints=[geom.asPoint()]
                newCroquis.type=newCroquis.CroquisType.Point
            else :
                newCroquis.type=newCroquis.CroquisType.Vide
                    
            for pt in geomPoints:
                pt=transformer.transform(pt)
                newCroquis.addPoint(Point(pt.x(),pt.y()))
            
        except Exception as e:
            self.logger.error(u"in makeCroquis:"+e.message)
            return None
        
        
        #croquisAndCentroid.append([newCroquis,centroid])

        return newCroquis
    
    
    
    def getPositionRemarque(self,listCroquis):
        """Recherche et retourne la position de la remarque (point).
        La position est calculée à partir des croquis associés à la remarque
        """
            
        #crée la table temporaire dans spatialite et calcule les centroides de chaque croquis
        res=self._createTempCroquisTable(listCroquis)
            
        #trouve le barycentre de l'ensemble des centroïdes
        if type(res)==list:
            barycentre= self._getBarycentre()
            #position= self._getNearestPoint(barycentre,listPoints)
            return barycentre
        else:               
            return None
      
            
    
    def _createTempCroquisTable(self,listCroquis):
        """Crée une table temporaire dans sqlite pour les nouveaux croquis
        La table contient la géométrie des croquis au format texte (WKT).
        Retourne la liste des points des croquis
        
        :param listCroquis : la liste des nouveaux croquis
        :type listCroquis: list
        
        :return une liste contenant tous les points des croquis
        :rtype: list de Point
        """
        
        dbName = self.projectFileName +"_RIPART"
        self.dbPath = self.projectDir+"/"+dbName+".sqlite"
        
        tmpTable ="tmpTable"
        
        allCroquisPoints=[]
        
        if len(listCroquis)==0:
            return None
        
        cr= listCroquis[0]
        geomType="POLYGON"
 
        if cr.type==cr.CroquisType.Ligne:
            geomType="LINESTRING"
        elif cr.type==cr.CroquisType.Polygone:
            geomType="POLYGON"
            
        try:
            self.conn= db.connect(self.dbPath)
            cur = self.conn.cursor()
            
            sql=u"Drop table if Exists "+tmpTable
            cur.execute(sql)
            
            sql=u"CREATE TABLE "+tmpTable+" (" + \
                u"id INTEGER NOT NULL PRIMARY KEY, textGeom TEXT, centroid TEXT)"  
            cur.execute(sql)
            
            i=0
            for cr in listCroquis: 
                i+=1
                if cr.type==cr.CroquisType.Ligne:
                    #geomType="LINESTRING"
                    textGeom="LINESTRING("
                    textGeomEnd=")"
                elif cr.type==cr.CroquisType.Polygone:
                    #geomType="POLYGON"   
                    textGeom="POLYGON(("
                    textGeomEnd="))"                 
                elif cr.type==cr.CroquisType.Point:
                    #geomType="POINT"
                    textGeom="POINT("
                    textGeomEnd=")"
                
                for pt in cr.points:       
                    textGeom +=  str(pt.longitude) + " " + str(pt.latitude)+","
                    allCroquisPoints.append(pt)
                    
                textGeom = textGeom[:-1] + textGeomEnd
 
                sql="INSERT INTO "+ tmpTable + "(id,textGeom,centroid) VALUES ("+ str(i) + ",'"+ textGeom +"',"+\
                    "AsText(centroid( ST_GeomFromText('"+ textGeom +"'))))"
                cur.execute(sql)

            self.conn.commit()
            
            
            #calculate the posiotin of the remark
            # position= self.getPositionRemarque(listCroquis,allCroquisPoints,self.conn)
           
        except Exception as e:
            self.logger.error("createTempCroquisTable "+e.message)
            return False
        finally:
            cur.close()
            self.conn.close()         
            
        return allCroquisPoints
            
        
    
        
    def _getBarycentre(self):    
        tmpTable ="tmpTable" 
        point=None
        try:
            dbName = self.projectFileName +"_RIPART"
            self.dbPath = self.projectDir+"/"+dbName+".sqlite"
            self.conn= db.connect(self.dbPath)
            cur = self.conn.cursor()
            
            sql ="SELECT X(ST_GeomFromText(centroid)) as x, Y(ST_GeomFromText(centroid)) as y  from "  + tmpTable 
            cur.execute(sql)
            
            rows = cur.fetchall()
            sumX=0
            sumY=0
            
            for row in rows:
                sumX+=row[0]
                sumY+=row[1]
            
            ptX= sumX/float(len(rows))
            ptY= sumY/float(len(rows))
            
            barycentre= Point(ptX,ptY)
            
            """ 
            #trouver le point le plus proche du barycentre
            sql ="SELECT textGeom  from "  + tmpTable 
            cur.execute(sql)
            
            nearestDist=-1
            nearestPoint=barycentre
           
            for row in rows:
                dist=math.hypot(row[0]-barycentre.longitude, row[1]-barycentre.latitude)
                if nearestDist<0 or dist<nearestDist:
                    nearestDist=dist
                    nearestPoint=Point(row[0],row[1])
             """   
            
            
        except Exception as e:
            self.logger.error("getBarycentre "+e.message)
            point=None
        
        return barycentre
    
    """def _getNearestPoint(self,barycentre, ptsList):
        pass
    """
    
    def getMapCoordReferenceSystem(self):
        mapCrs=self.mapCan.mapRenderer().destinationCrs().authid()
        refSys=QgsCoordinateReferenceSystem(mapCrs)
        
        return refSys
    
    
    
    ## magicwand
    
    def oneCroquisOrRemarkSelected(self):
        cntSelectedCroquis=0
        cntSelectedRemarks=0
        mapLayers = self.mapCan.layers() 
        
        for cr in RipartHelper.croquis_layers:
            crLay= self.getLayerByName(cr)
            cntSelectedCroquis+=len(crLay.selectedFeatures())
            
        remLay= self.getLayerByName(RipartHelper.nom_Calque_Remarque)
        
        cntSelectedRemarks+=len(remLay.selectedFeatures())
        
        message1="Veuillez ne sélectionner qu'une seule Remarque"
        
        if cntSelectedCroquis>1 or cntSelectedRemarks>1:
            pass 
        
    
    def getSelectedRipartFeatures(self):
        #key: layer name, value: noRemarque
        croquisLays={}
        
        remNos=""
        
        mapLayers = self.mapCan.layers() 
        
        for l in mapLayers:
            if l.name() in RipartHelper.croquis_layers and len(l.selectedFeatures())>0:
                croquisLays[l.name()]=  []
                for feat in l.selectedFeatures():
                    idx= l.fieldNameIndex("NoRemarque")
                    noRemarque= feat.attributes()[idx]
                    remNos+=str(noRemarque)+","
                    croquisLays[l.name()].append(feat.id())
                    

        remarqueLay=self.getLayerByName(RipartHelper.nom_Calque_Remarque) 
        feats=remarqueLay.selectedFeatures()
        
        for f in feats:
            idx= remarqueLay.fieldNameIndex("NoRemarque")
            noRemarque= f.attributes()[idx]
          
            remNos+=str(noRemarque)+","
            croquisLays=self.getCroquisForRemark(noRemarque,croquisLays)
        
       
        self.selectRemarkByNo(remNos[:-1])
        
        for cr in croquisLays:
            lay=self.getLayerByName(cr) 
            lay.setSelectedFeatures( croquisLays[cr])
        
    
       
    
    
        
    def selectRemarkByNo(self,noRemarques):
        
        self.conn= db.connect(self.dbPath)
        cur = self.conn.cursor()
        
        table=RipartHelper.nom_Calque_Remarque
        lay=self.getLayerByName(table) 
        
        sql="SELECT * FROM " + table +"  WHERE noRemarque in (" + noRemarques +")"
        rows=cur.execute(sql)       
            
        featIds=[]
            
        for row in rows:
            print row[0]
            featIds.append(row[0])
           

        lay.setSelectedFeatures( featIds )
        
       
        
       
    
    def getCroquisForRemark(self,noRemarque,croquisSelFeats):
       
        crlayers= RipartHelper.croquis_layers
        
        self.conn= db.connect(self.dbPath)
        cur = self.conn.cursor()
        
        for table in crlayers:
            sql="SELECT * FROM " + table +"  WHERE noRemarque= " + str(noRemarque)
            rows=cur.execute(sql)       
            
            featIds=[]
            
            for row in rows:
                featIds.append(row[0])
                if not table in  croquisSelFeats:
                    croquisSelFeats[table]=[]
                croquisSelFeats[table].append(row[0])
            
  
        return croquisSelFeats   