# -*- coding: utf-8 -*-
'''
Created on 29 sept. 2015

@author: AChang-Wailing
'''

from qgis.utils import *

from PyQt5 import QtGui
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.core import QgsCoordinateReferenceSystem, QgsMessageLog, QgsFeatureRequest,QgsCoordinateTransform,\
                      QgsGeometry,QgsDataSourceUri,QgsVectorLayer,QgsProject, QgsPolygon
                      
from .RipartException import RipartException

import os.path
import shutil
import ntpath
from qgis.utils import spatialite_connect
import sqlite3 as sqlite
import configparser

from  .RipartHelper import  RipartHelper
from .core.RipartLoggerCl import RipartLogger
from .core.Profil import Profil
from .core.Client import Client
from .core.ClientHelper import ClientHelper
from .core.Attribut import Attribut
from .core.Point import Point
from .core.Croquis import Croquis
from .FormConnexion_dialog import FormConnexionDialog
from .FormInfo import FormInfo
from .core import ConstanteRipart as cst


class Contexte(object):
    """
    Contexte et initialisation de la "session" 
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
    
    #proxy
    proxy = None
    
    #le logger
    logger=None
    
    
    def __init__(self, QObject,QgsProject):
        '''
        Constructor
        
        Initialisation du contexte
        ''' 
        self.QObject=QObject
        self.QgsProject= QgsProject
        self.mapCan = QObject.iface.mapCanvas()
        
        self.iface= QObject.iface
        
        self.login=""
        self.pwd=""
        self.urlHostRipart=""
        
        self.profil = None
        self.ripClient = None
        
        self.logger=RipartLogger("Contexte").getRipartLogger()
  
        self.spatialRef = QgsCoordinateReferenceSystem( RipartHelper.epsgCrs, QgsCoordinateReferenceSystem.EpsgCrsId)
        
        #version in metadata
        cst.RIPART_CLIENT_VERSION = self.getMetadata('general','version')
        
        try:
            #set du répertoire et fichier du projet qgis
            self.setProjectParams(QgsProject)
            
            #contrôle l'existence du fichier de configuration
            self.checkConfigFile()      

            #set de la base de données
            self.getOrCreateDatabase()
            
            #set des fichiers de style
            self.copyRipartStyleFiles()
            
            #retrouve les formats de fichiers joints acceptés à partir du fichier formats.txt. 
            formatFile =open( os.path.join(self.plugin_path,'files','formats.txt'), 'r')      
            lines=formatFile.readlines()
            self.formats=[x.split("\n")[0] for x in lines]  
            
            '''Deprecated
            try:
            #Appel à un service pour obtenir les formats autorisés. Ce service n'existe plus, mais possible que dans 
            #le futur un nouveau service soit créé
                formatFile =urllib.urlopen('http://ripart.ign.fr/?page=doctype')
                if formatFile.code!=200:
                    raise
                
                lines=formatFile.readlines()
                self.formats=[x.split("\t")[0] for x in lines]
                
                if self.formats[0].startswith("<!DOCTYPE html") :
                    raise
                
            except Exception as e:
                self.logger.error("init contexte:" + format(e))
                formatFile =open( os.path.join(self.plugin_path,'files','formats.txt'), 'r')      
                lines=formatFile.readlines()
                self.formats=[x.split("\n")[0] for x in lines]  '''    
          
        except Exception as e:
            self.logger.error("init contexte:" + format(e))
            raise
    
    def getMetadata(self,category, param):
       
        config = configparser.RawConfigParser()
        config.read(self.plugin_path + '\\metadata.txt')
        return config.get('general', 'version')
    
   
    
    @staticmethod    
    def getInstance(QObject=None,QgsProject=None):
        """Retourne l'instance du Contexte
        """
        if not Contexte.instance:
            Contexte.instance=Contexte._createInstance(QObject,QgsProject)
          
        elif  (Contexte.instance.projectDir!= QgsProject.instance().homePath() or
              ntpath.basename(QgsProject.instance().fileName()) not in [Contexte.instance.projectFileName+".qgs",Contexte.instance.projectFileName+".qgs.qgz"]) :       
            Contexte.instance=Contexte._createInstance(QObject,QgsProject)

        return Contexte.instance
    
    
    
    @staticmethod   
    def _createInstance(QObject,QgsProject):
        """Création de l'instance du contexte
        """
        try:
            Contexte.instance = Contexte(QObject,QgsProject)
            Contexte.instance.logger.debug("nouvelle instance de contexte créée" )
        except Exception as e:
            Contexte.instance=None
            return None
        
        return Contexte.instance
    
    
    
    def setProjectParams(self,QgsProject):
        """set des paramètres du projet
        """
        self.projectDir=QgsProject.instance().homePath()
        
        if self.projectDir =="":    
            RipartHelper.showMessageBox(u"Votre projet QGIS doit être enregistré avant de pouvoir utiliser l'extension RIPart")
            raise Exception(u"Projet QGIS non enregistré") 
    
        #nom du fichier du projet enregistré
        fname=ntpath.basename(QgsProject.instance().fileName())
        
        self.projectFileName= fname[:fname.find(".")]
        
    
    
    def checkConfigFile(self):
        """Contrôle de l'existence du fichier de configuration
        """
        ripartxml=self.projectDir+os.path.sep+ RipartHelper.nom_Fichier_Parametres_Ripart
        if not os.path.isfile(ripartxml) :
            try:
                shutil.copy(self.plugin_path+os.path.sep+RipartHelper.ripart_files_dir+os.path.sep+ RipartHelper.nom_Fichier_Parametres_Ripart,
                             ripartxml)
                self.logger.debug("copy ripart.xml" )
            except Exception as e:
                self.logger.error("no ripart.xml found in plugin directory" + format(e))
                raise Exception("Le fichier de configuration "+ RipartHelper.nom_Fichier_Parametres_Ripart + " n'a pas été trouvé.")
           
       
    
    def copyRipartStyleFiles(self):
        """Copie les fichiers de styles (pour les remarques et croquis ripart)
        """
        styleFilesDir=self.projectDir + os.path.sep + RipartHelper.qmlStylesDir
        
        RipartHelper.copy(self.plugin_path + os.path.sep + RipartHelper.ripart_files_dir + os.path.sep + RipartHelper.qmlStylesDir,
                          styleFilesDir)
        
  
  
     
    def getConnexionRipart(self,newLogin=False):
        """Connexion au service ripart 
        
        :param newLogin: booléen indiquant si on fait un nouveau login (fonctionalité "Connexion au service Ripart")
        :type newLogin: boolean
        
        :return 1 si la connexion a réussie, 0 si elle a échouée, -1 s'il y a eu une erreur (Exception)
        :rtype int
        """
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
        
        xmlproxy = RipartHelper.load_ripartXmlTag(self.projectDir,RipartHelper.xml_proxy,"Serveur").text
        if (xmlproxy!= None and str(xmlproxy).strip()!='' ):     
            self.proxy ={'https': str(xmlproxy).strip()}
        else :
            self.proxy = None
        
        if (self.login =="" or self.pwd=="" or newLogin):
            self.loginWindow.setLogin(self.login)
            self.loginWindow.exec_()

            while (result<0):      
                if self.loginWindow.cancel:
                    # fix_print_with_import
                    print("rejected")
                    self.loginWindow = None
                    result=0
                elif self.loginWindow.connect :
                    # fix_print_with_import
                    print("connect")
                    self.login = self.loginWindow.getLogin()
                    self.pwd=self.loginWindow.getPwd()
                    print("login " + self.login)
                    try: 
                        client = Client(self.urlHostRipart, self.login, self.pwd,self.proxy)
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
                                self.logger.debug("result 1")
                        else :
                            # fix_print_with_import
                            print("error")
                    except Exception as e:
                        result=-1
                        self.pwd=""
                        self.logger.error(format(e))        
                        
                        try:
                            self.loginWindow.setErreur(ClientHelper.getEncodeType(format(e)))
                        except Exception as e2:
                            self.loginWindow.setErreur(ClientHelper.getEncodeType("la connexion a échoué"))
                        self.loginWindow.exec_()
                        
        else: 
            try: 
                client = Client(self.urlHostRipart, self.login, self.pwd, self.pwd,self.proxy)   
                result=1
                self.client=client
            except RipartException as e:
                # fix_print_with_import
                print(format(e))
                result=-1
        
        if result ==1:
            self.logger.debug("result 1 b")
            self.ripClient = client
            self.logger.debug("ripclient")
        
        return result
    
    

    def saveLogin(self,login):
        """Sauvegarde du login dans le contexte et dans le fichier ripart.xml
        """
        self.login=login
        RipartHelper.save_login( self.projectDir, login)
    
   
    def getOrCreateDatabase(self):
        """Retourne la base de données spatialite contenant les tables des remarques et croquis
        Si la BD n'existe pas, elle est créée
        
        """
        dbName = self.projectFileName +"_RIPART"
        self.dbPath = self.projectDir+"/"+dbName+".sqlite"
        
        createDb=False
            
        if not os.path.isfile(self.dbPath) :
            createDb=True
            try:
                shutil.copy(self.plugin_path + os.path.sep + RipartHelper.ripart_files_dir + os.path.sep + RipartHelper.ripart_db,
                             self.dbPath)
                self.logger.debug("copy ripart.sqlite" )
            except Exception as e:
                self.logger.error("no ripart.sqlite found in plugin directory" + format(e))
                raise e
        try:    
            self.conn = spatialite_connect(self.dbPath)
    
            # creating a Cursor
            cur = self.conn.cursor()
           
            sql="SELECT name FROM sqlite_master WHERE type='table' AND name='Signalement'"  
            cur.execute(sql)       
            if cur.fetchone() ==None:
                #create layer Signalement
                RipartHelper.createRemarqueTable(self.conn)
            
            for lay in RipartHelper.croquis_layers:  
                sql="SELECT name FROM sqlite_master WHERE type='table' AND name='"+lay+"'"
                cur.execute(sql)       
                if cur.fetchone() ==None:
                    #create layer 
                    RipartHelper.createCroquisTable(self.conn,lay,RipartHelper.croquis_layers[lay])
                    
        except RipartException as e:
            self.logger.error(format(e))
            raise
        finally:
            cur.close()
            self.conn.close()
        
      
      
      
    def addRipartLayersToMap(self):
        """Add ripart layers to the current map 
        """
        
        uri =QgsDataSourceUri()
 
        dbName = self.projectFileName +"_RIPART"
        self.dbPath = self.projectDir+"/"+dbName+".sqlite"
        uri.setDatabase(self.dbPath)
        self.logger.debug(uri.uri())
        
        maplayers=self.getAllMapLayers()
        
        root = self.QgsProject.instance().layerTreeRoot()
        
        for table in RipartHelper.croquis_layers_name: 
            if table not in maplayers:
                uri.setDataSource('',  table, 'geom')
                uri.setSrid('4326')
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite') 
                vlayer.setCrs(QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                QgsProject.instance().addMapLayer(vlayer,False)
                                
                root.insertLayer(0,vlayer)
                
                self.logger.debug("Layer "+vlayer.name() + " added to map")          
                
                #ajoute les styles aux couches
                style= os.path.join(self.projectDir, "ripartStyles",table+".qml")
                vlayer.loadNamedStyle(style)
        
        self.mapCan.refresh()
        
          
  
    def getAllMapLayers(self):
        """Return the list of layer names which are loaded in the map
        
        :return dictionnaire des couches chargées sur la carte (key: layer name, value: layer id)
        :rtype dictionary
        """
        
        layers = QgsProject.instance().mapLayers()

        layerNames=[]
        maplayers={}
        for key in layers:
            l=layers[key]
            layerNames.append(l.name())
            maplayers[l.name()]= l.id()
        
        return maplayers
    
    
    
    def getMapPolygonLayers(self):
        """Retourne les calques qui sont de type polygon ou multipolygon
        
        :return dictionnaire des couches de type polygon(key: layer id, value: layer name)
        :rtype dictionary
        """
        layers = QgsProject.instance().mapLayers()
        
        polylayers={}
        
        for key in layers:
            l=layers[key]
            
            if type(l) is QgsVectorLayer and l.geometryType ()!=None and l.geometryType ()==QgsPolygon :
                polylayers[l.id()]=l.name()
                
        return polylayers
 
    
    def getLayerByName(self,layName):
        """Retourne le calque donné par son nom
        
        :param layName: le nom du calque 
        :type layName: string
        
        :return: le premier calque ayant pour nom celui donné en paramètre
        :rtype: QgsVectorLayer
        """
        mapByName= QgsProject.instance().mapLayersByName(layName)
        if len(mapByName) >0:
            return mapByName[0]
        else:
            return None
        
      
    def emptyAllRipartLayers(self):
        """Supprime toutes les remarques, vide les tables de la base ripart.sqlite 
        """
        ripartLayers= RipartHelper.croquis_layers
        ripartLayers[RipartHelper.nom_Calque_Signalement]="POINT"
              
        try:       
            self.conn = spatialite_connect(self.dbPath)
            
            for table in ripartLayers:
                RipartHelper.emptyTable(self.conn, table)
                
            ripartLayers.pop(RipartHelper.nom_Calque_Signalement,None)
             
            self.conn.commit()    
        except RipartException as e:
            self.logger.error(format(e))
            raise
        finally:
            self.conn.close()
        
        self.refresh_layers()
        
        
        
    def refresh_layers(self):
        """Rafraichissement de la carte
        """
        for layer in self.mapCan.layers():
            layer.triggerRepaint()


     
    def updateRemarqueInSqlite(self,rem):
        """Met à jour une remarque (après l'ajout d'une réponse) 
        
        :param rem : la remarque à mettre à jour
        :type rem: Remarque
        """
        try:
            #self.conn= sqlite3.connect(self.dbPath)
            self.conn = spatialite_connect(self.dbPath)
                          
            sql = "UPDATE "+ RipartHelper.nom_Calque_Signalement+" SET "
            sql += " Date_MAJ= '" + rem.getAttribut("dateMiseAJour") +"'," 
            sql += " Date_validation= '" + rem.getAttribut("dateValidation") +"'," 
            sql += " Réponses= '" + ClientHelper.getValForDB(rem.concatenateReponse()) +"', "
            sql += " Statut='" + rem.statut  +"' "
            sql += " WHERE NoSignalement = " + rem.id
             
            cur= self.conn.cursor()
            cur.execute(sql)
            
            self.conn.commit()
            
        except Exception as e :
            self.logger.error(format(e))
            raise
        finally:
            cur.close()
            self.conn.close()
        
   
    
    def countRemarqueByStatut(self,statut): 
        """Retourne le nombre de remarques ayant le statut donné en paramètre
        
        :param statut: le statut de la remarque (=code renvoyé par le service)
        :type statut: string
        """ 
        remLay=self.getLayerByName(RipartHelper.nom_Calque_Signalement)
        expression='"Statut" = \''+ statut +'\''
        filtFeatures=remLay.getFeatures(QgsFeatureRequest().setFilterExpression( expression ))
        return len(list(filtFeatures))
    
    
    
    #############Création nouvelle remarque ###########
    
    def hasMapSelectedFeatures(self):
        """Vérifie s'il y a des objets sélectionnés
        
        :return true si de objets sont sélectionnés, false sinon
        :rtype boolean
        """
        mapLayers = self.mapCan.layers()
        for l in mapLayers:
            if type(l) is QgsVectorLayer and len(l.selectedFeatures())>0:
                return True        
        return False    

    
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
            if type(l) is not QgsVectorLayer:
                continue
            for f in l.selectedFeatures():
                fattributes= f.attributes()
              
                #la liste des croquis
                croquiss=[]
                
                #le type du feature
                ftype= f.geometry().type()
        
                geom= f.geometry()
                
                isMultipart= geom.isMultipart()
                
                #if geom.isMultipart() => explode to single parts
                if isMultipart and ftype==qgis.core.Polygon:
                    for poly in geom.asMultiPolygon():
                        croquiss.append(self.makeCroquis(QgsGeometry.fromPolygon(poly),qgis.core.Polygon,l.crs(),f[0]))
                        
                elif isMultipart and ftype==qgis.core.Line:
                    for line in geom.asMultiPolyline():
                        croquiss.append(self.makeCroquis(QgsGeometry.fromPolyline(line),qgis.core.Line,l.crs(),f[0]))              
               
                elif isMultipart and ftype==qgis.core.Point:
                    for pt in geom.asMultiPoint():
                        croquiss.append(self.makeCroquis(QgsGeometry.fromPoint(pt),qgis.core.Point,l.crs(),f[0]))       
                else :    
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
        newCroquis= Croquis()
        geomPoints=[]        
       
        try:
            destCrs=QgsCoordinateReferenceSystem(RipartHelper.epsgCrs)
                       
            transformer = QgsCoordinateTransform(layerCrs, destCrs)

            if ftype==qgis.core.Polygon:
                geomPoints=geom.asPolygon()
                if len(geomPoints)>0:
                    geomPoints=geomPoints[0]      #les points du polygone
                else: 
                    self.logger.debug(u"geomPoints problem " + str(fId))        
                newCroquis.type=newCroquis.CroquisType.Polygone
                
            elif ftype==qgis.core.Line:
                geomPoints = geom.asPolyline()
                newCroquis.type=newCroquis.CroquisType.Ligne
            
            elif ftype==qgis.core.Point:
                geomPoints=[geom.asPoint()]
                newCroquis.type=newCroquis.CroquisType.Point
            else :
                newCroquis.type=newCroquis.CroquisType.Vide
                    
            for pt in geomPoints:
                pt=transformer.transform(pt)
                newCroquis.addPoint(Point(pt.x(),pt.y()))
            
        except Exception as e:
            self.logger.error(u"in makeCroquis:"+format(e))
            return None
        
     
        return newCroquis
    
    
    
    def getPositionRemarque(self,listCroquis):
        """Recherche et retourne la position de la remarque (point).
        La position est calculée à partir des croquis associés à la remarque
        
        :param listCroquis: la liste des croquis
        :type listCroquis: list de Croquis
        
        :return la position de la remarque 
        :rtype Point
        """
            
        #crée la table temporaire dans spatialite et calcule les centroides de chaque croquis
        res=self._createTempCroquisTable(listCroquis)
            
        #trouve le barycentre de l'ensemble des centroïdes
        if type(res)==list:
            barycentre= self._getBarycentre()
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
      
        try:
            #self.conn= sqlite3.connect(self.dbPath)
            self.conn = spatialite_connect(self.dbPath)
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
                    textGeom="LINESTRING("
                    textGeomEnd=")"
                elif cr.type==cr.CroquisType.Polygone:
                    textGeom="POLYGON(("
                    textGeomEnd="))"                 
                elif cr.type==cr.CroquisType.Point:
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
            
   
        except Exception as e:
            self.logger.error("createTempCroquisTable "+format(e))
            return False
        finally:
            cur.close()
            self.conn.close()         
            
        return allCroquisPoints
            
        
    
        
    def _getBarycentre(self):   
        """Calcul du barycentre de l'ensemble des croquis à partir des centroides de chaque croquis;
        ces centroides sont stockés dans la table temporaire "tmpTable"
        
        :return: le barycentre
        :rtype: Point
        """ 
        tmpTable ="tmpTable" 
        point=None
        try:
            dbName = self.projectFileName +"_RIPART"
            self.dbPath = self.projectDir+"/"+dbName+".sqlite"
            #self.conn= sqlite3.connect(self.dbPath)
            self.conn = spatialite_connect(self.dbPath)
            
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
       
        except Exception as e:
            self.logger.error("getBarycentre "+format(e))
            point=None
        
        return barycentre
    
  
    
    ################### magicwand  ##################################################
   
        
    def selectRemarkByNo(self,noSignalements):
        """Sélection des remarques données par leur no
        
        :param noSignalements : les no de signalements à sélectionner
        :type noSignalements: list de string
        """
        
        #self.conn= sqlite3.connect(self.dbPath)
        self.conn = spatialite_connect(self.dbPath)
        cur = self.conn.cursor()
        
        table=RipartHelper.nom_Calque_Signalement
        lay=self.getLayerByName(table) 
        
        sql="SELECT * FROM " + table +"  WHERE noSignalement in (" + noSignalements +")"
        rows=cur.execute(sql)       
            
        featIds=[]
            
        for row in rows:
            # fix_print_with_import
            print(row[0])
            featIds.append(row[0])
           
        lay.setSelectedFeatures( featIds )
        
       
  
    
    def getCroquisForRemark(self,noSignalement,croquisSelFeats):
        """Retourne les croquis associés à une remarque
        
        :param noSignalement: le no de la remarque 
        :type noSignalement: int
        
        :param ccroquisSelFeats: dictionnaire contenant les croquis 
                                 (key: le nom de la table du croquis, value: liste des identifiants de croquis) 
        :type croquisSelFeats: dictionnary
        
        :return: dictionnaire contenant les croquis 
        :rtype: dictionnary
        """    
        crlayers= RipartHelper.croquis_layers
        
        #self.conn= sqlite3.connect(self.dbPath)
        self.conn = spatialite_connect(self.dbPath)
        cur = self.conn.cursor()
        
        for table in crlayers:
            sql="SELECT * FROM " + table +"  WHERE noSignalement= " + str(noSignalement)
            rows=cur.execute(sql)       
            
            featIds=[]
            
            for row in rows:
                featIds.append(row[0])
                if not table in  croquisSelFeats:
                    croquisSelFeats[table]=[]
                croquisSelFeats[table].append(row[0])
            
        return croquisSelFeats   