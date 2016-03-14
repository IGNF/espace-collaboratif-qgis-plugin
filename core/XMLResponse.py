# -*- coding: utf-8 -*-
'''
Created on 26 janv. 2015

@author: AChang-Wailing
'''

import xml.etree.ElementTree as ET
from Profil import Profil
import ConstanteRipart as cst
from Remarque import Remarque
from Theme import Theme
from Point import Point
from Auteur import Auteur
from Croquis import Croquis
from Groupe import  Groupe
from Attribut import Attribut
from GeoReponse import GeoReponse
from datetime import datetime
from ClientHelper import ClientHelper
from RipartLoggerCl import RipartLogger

class XMLResponse(object):
    """
    Classe pour le parsing des réponses xml et l'extraction des informations nécessaires
    """
    
    #la réponse du serveur (au format xml)
    response =""
    
    # racine du document xml
    root=""
    

    logger=RipartLogger("ripart.XMLResponse").getRipartLogger()
    

    def __init__(self, response):
        """Constructeur
        
        :param response: la réponse du serveur (xml)
        :type response: string 
        """
        """if type(response)==type('str'):
            self.response = response
        else :
            self.response = response.encode('utf-8');"""
            
        self.response =ClientHelper.stringToStringType(response)
        
        try:
            self.root =ET.fromstring(self.response)
        except Exception as e:
            self.logger.error(str(e))
         
        
        self.logger.debug("init")
        
        
            
    def checkResponseValidity(self):
        """Contrôle la validité de la réponse. 
        
        Si le code erreur="OK", la réponse est valide
        :return un dictionnaire à 2 clés, message et code
        """ 
       
        errMessage ={'message':'', 'code':''}
        
        try:     
            erreur= self.root.findall('./REPONSE/ERREUR')
            
            for m in erreur:
                errMessage['message']=m.text
                errMessage['code']=m.attrib['code']
  
        except KeyError as e:
            self.logger.error(str(e))
           
        except Exception as e:
            self.logger.error(str(e))
          
            
        return errMessage
   
     
   
    def getAleas(self):
        """ Extraction des Aleas       
        :return une liste contenant les 2 aleas
        """
        
        aleas= list()
        
        try:        
            alea1= self.root.find('./REPONSE/ALEA1')           
            aleas.append(alea1.text)
            
            alea2= self.root.find('./REPONSE/ALEA2')    
            aleas.append(alea2.text)
            
        except Exception as e:            
            self.logger.error(str(e))
            raise Exception('Probl�me de connexion')
 
        return aleas
 
    
    
   
    def getConnectValues(self):
        """Extraction des paramètres de connexion
        
        :return: un dictionnaire contenant les paramètres de connexion (ID_AUTEUR, JETON, SITE)
        """
        connectValues = {'ID_AUTEUR':None,'JETON':None, 'SITE':None}
        
        try:      
            id_auteur =self.root.find('./REPONSE/ID_AUTEUR')    
            if id_auteur is not None:           
                connectValues['ID_AUTEUR'] =id_auteur.text
            else:
                raise Exception("ID_AUTEUR inexistant dans la r�ponse xml")
                         
            jeton=connectValues['JETON'] =self.root.find('./REPONSE/JETON')          
            if jeton is not None:
                connectValues['JETON'] =jeton.text
            else:
                raise Exception("JETON inexistant dans la réponse xml")
            
            
            site = connectValues['SITE']= self.root.find('./REPONSE/SITE')
            if site is not None:
                connectValues['SITE'] = site.text
            else:
                raise Exception("SITE inexistant dans la réponse xml")
                        
        except Exception as e:            
            self.logger.error(str(e))
            raise 
             
        return connectValues
        
    
  
    def getCurrentJeton(self):
        """Extraction du nouveau jeton
           
        :return le jeton
        """
        
        jeton="" 
         
        try:
            jetonNode =self.root.find('./REPONSE/JETON')
            
            if jetonNode is not None:
                jeton = jetonNode.text            
            else:
                raise Exception('Pas de jeton')
            
        except Exception as e:            
            self.logger.error('getCurrentJeton:' + str(e) )
            raise
            
        return jeton
                
                
     
    def extractProfil(self):
        """Extraction du profil à partir de la réponse xml
        
        :return: profil de l'utilisateur
        """     
             
        profil = Profil()
        
        try:
            #aut= Auteur()
            node =self.root.find('./AUTEUR/NOM') 
            profil.auteur.nom =node.text
            
            node =self.root.find('./PROFIL/ID_GEOPROFIL')  
            profil.id_Geoprofil = node.text
            
            node =self.root.find('./PROFIL/TITRE')
            profil.titre = node.text
            
            node =self.root.find('./PROFIL/ZONE')
            profil.zone = cst.ZoneGeographique.__getitemFromString__(node.text)
            
            gr = Groupe()
            node =self.root.find('./PROFIL/ID_GEOGROUPE')
            gr = node.text
            
            node =self.root.find('./PROFIL/GROUPE')
            profil.geogroupe.nom= node.text
            
            node =self.root.find('./PROFIL/ID_GEOGROUPE')
            profil.geogroupe.id= node.text
               
            node =self.root.find('./PROFIL/LOGO')
            profil.logo= node.text
            
            node =self.root.find('./PROFIL/FILTRE')
            profil.filtre = node.text
            
            node =self.root.find('./PROFIL/PRIVE')
            profil.prive = True if node.text==1 else False
                    
            #va chercher les thèmes associés au profil      
            themes= self.getThemes()
            profil.themes = themes
            
        except Exception as e:            
            self.logger.error('extractProfil:' + str(e) )
            raise
            
        return profil
        
        
    
    def getThemes(self):
        """Extraction des thèmes associés au profil     
        :return les thèmes 
        """
        
        themes=[]
       
        try:            
            nodes =self.root.findall('THEMES/THEME')      
    
            for node in nodes :
                theme = Theme()
                theme.groupe= Groupe()       
                theme.groupe.nom = (node.find('NOM')).text
                theme.groupe.id = (node.find('ID_GEOGROUPE')).text                         
                themes.append(theme)
                
        except Exception as e:
            self.logger.error(str(e) )
            raise Exception ("Erreur dans la récupération des thèmes du profil")
            
        return themes
    

    
    def getVersion(self):
        """Retourne la version du service ripart    
        :return la version du service
        """
        
        v=""     
        try:
            v=  self.root.attrib['version']
            
        except KeyError as e:
            self.logger.error(str(e))
           
        except Exception as e:
            self.logger.error(str(e)) 
        
        return v
    
    
    
    def getDate(self):
        """Retourne la date de la réponse xml
        """
        try:
            node = self.root.find('PAGE/DATE')
            date = node.text
        except Exception as e:
            self.logger.error('getTotalResponse :'+ str(e))
        
        return date
    
    
    def getTotalResponse(self):
        """Retourne le nombre total de réponses
        :return: nombre total de réponse
        """       
        total=0
        try:
            node = self.root.find('PAGE/TOTAL')
            total = node.text
        except Exception as e:
            self.logger.error('getTotalResponse :'+ str(e))
        
        return total
        
           
        
    
    def extractRemarques(self):
        """Extraction des remarques de la réponse xml
        
        :param remarques: dictionnaire  de remarques
        :type remarques: Dictionary of Remarque (key: identifiant de la ramarque, value: la remarque
        :return: dictionnaire de remarques (dans l'ordre inverse d'identifiants)
        """
        
        remarques= {}      
        
        try:
            georems= self.root.findall('GEOREM')
            
            for node in georems :
                
                rem= Remarque()
                themes = []
                
                rem.id= (node.find('ID_GEOREM')).text
                
                
                nfind=node.find('AUTORISATION')
                if nfind !=None:
                    rem.autorisation= nfind.text              
              
                for th in node.findall('THEME'):                    
                    nomGroupe = (th.find('NOM')).text
                    idGroupe = (th.find('ID_GEOGROUPE')).text
                    
                    theme = Theme()
                    theme.groupe = Groupe(idGroupe, nomGroupe)
                    themes.append(theme)
                    
                rem.themes= themes
                
                nfind=node.find('LIEN')
                if nfind !=None:
                    rem.lien = nfind.text
                    rem.lien.replace("&amp;" , "&");
                
                nfind=node.find('LIEN_PRIVE')
                if nfind!=None:
                    rem.lienPrive = nfind.text
                    rem.lienPrive.replace("&amp;" , "&");
                
                nfind=node.find('DATE')
                if nfind!=None:
                    rem.dateCreation= nfind.text
                
                nfind=node.find('MAJ')
                if nfind!=None:
                    rem.dateMiseAJour=nfind.text
                
                nfind=node.find('DATE_VALID')
                if nfind!=None:                   
                    rem.dateValidation=nfind.text
                
                lon =(node.find('LON')).text
                lat= (node.find('LAT')).text
                rem.position = Point(lon,lat)
                
                nfind=node.find('STATUT')
                if nfind!=None:
                    rem.statut =nfind.text
                
                rem.departement= Groupe()
                nfind=node.find('ID_DEP')
                if nfind!=None:
                    rem.departement.id= nfind.text
                nfind=node.find('DEPARTEMENT')
                if nfind!=None:
                    rem.departement.nom =nfind.text
                
                nfind=node.find('COMMUNE')
                if nfind!=None:               
                    rem.commune= nfind.text
                
                nfind=node.find('COMMENTAIRE')
                if nfind!=None:
                    rem.commentaire= nfind.text
                
                
                rem.auteur = Auteur()
                nfind=node.find('ID_AUTEUR')
                if nfind !=None:
                    rem.auteur.id = nfind.text
                nfind=node.find('AUTEUR')
                if nfind!=None:
                    rem.auteur.nom =nfind.text
                
                rem.groupe =Groupe()
                nfind=node.find('ID_GEOGROUPE')
                if nfind!=None:
                    rem.groupe.id =nfind.text
                nfind=node.find('GROUPE')
                if nfind!=None:
                    rem.groupe.nom =nfind.text

                nfind=node.find('ID_PARTITION')
                if nfind !=None:
                    rem.id_partition=nfind.text
                
                #croquis
                rem = self.getCroquisForRem(rem, node)
                
                #documents
                rem = self.getDoc(rem, node)
                
                #réponses (GEOREP)
                rem= self.getGeoRep(rem,node)
                
                
                #rem.hash = (node.find('HASH')).text
                rem.source =(node.find('SOURCE')).text
                
                remarques[rem.id]=rem
                
                
        except Exception as e:
            self.logger.error(str(e))
            
            raise Exception("Une erreur est survenue dans l'importation des remarques")   
                
        
        return remarques
        
        
    def getNodeText(self,node):
        if node!=None:
            return node.text
        else:
            return ""
        
    def getCroquisForRem (self , rem, node):
        """ Extrait les croquis d'une remarque et les ajoute dans l'objet Remarque (rem)

        :param rem un objet Remarque
        :type rem: Remarque
        
        :param node: le noeud de la remarque dans le fichier xml (<GEOREM> ...</GEOREM>)
        :type node: string
        
        :return la remarque avec les croquis
        :rtype Remarque
        """
            
        objets= node.findall('CROQUIS/objet')

            
        for ob in objets:
            croquis = Croquis()
            croquis.type = ob.attrib['type']
            croquis.nom = ob.find('nom').text
            
            #attributs
            attributs= ob.findall('attributs/attribut')
            for att in attributs:
                attribut = Attribut()
                attribut.nom = att.attrib['name']
                attribut.valeur = att.text
                croquis.addAttribut(attribut)
                
            
            #géométrie
            coords= ob.iterfind('.//gml:coordinates',cst.namespace)
            coordinates=""
            for c in coords:
                pts=c.text.split(" ")
                for spt in pts:
                    pt= Point()
                    latlon=spt.split(",")  
                    if len(latlon)==4:
                        pt.longitude=float(latlon[0] + "."+latlon[1])
                        pt.latitude=float(latlon[2] + "."+latlon[3])
                    elif len(latlon)==2:
                        pt.longitude=float(latlon[0] )
                        pt.latitude=float(latlon[1] )
                      
                    if pt.longitude!=None and pt.latitude!=None:  
                        coordinates += str(pt.longitude) + " "+ str(pt.latitude) + ","
                        croquis.addPoint(pt) 
                    
            croquis.coordinates= coordinates[:-1]  

            #ajoute les croquis à la remarque
            rem.addCroquis(croquis)  
                   
        return rem
                
                
    def getDoc(self,rem,node):    
        """Extraction des documents attachés à une remarque
        
        :param rem un objet Remarque
        :type rem: Remarque
        
        :param node: le noeud de la remarque dans le fichier xml (<GEOREM> ...</GEOREM>)
        :type node: string
        
        :return la remarque avec les croquis
        :rtype Remarque
        """
        
        docs= node.findall('DOC')
        
        for doc in docs:
            rem.addDocument(doc)
            
        return rem
    
    
    def getGeoRep(self,rem,node):
        """Extraction des réponses d'une remarque
        """
        
        reponses = node.findall("GEOREP")
        
        for rep in reponses:
            georep = GeoReponse()
            
            gr = Groupe()
            gr.id = rep.find('ID_GEOREP').text
            gr.nom = rep.find('TITRE').text
            georep.groupe = gr
            
            georep.auteur=Auteur()
            georep.auteur.id = rep.find('ID_AUTEUR').text
            georep.auteur.nom = rep.find('AUTEUR').text
            
            georep.statut= cst.STATUT.__getitemFromString__(rep.find('STATUT').text)          
            georep.date= datetime.strptime(rep.find('DATE').text,"%Y-%m-%d %H:%M:%S")    
            georep.reponse = rep.find('REPONSE').text
        
            rem.addGeoReponse(georep)
            
        return rem
        
        
if __name__ == "__main__":
    
    x=  """<?xml version='1.0' encoding='UTF-8'?>
                            <geors version='0.1'>
                            <REPONSE type='action=connect'>
                                <ERREUR code='OK'>OK</ERREUR>
                                <ALEA1>6117245975489987c2c8028.02593919</ALEA1>
                                <ALEA2>141784489354899890b49555.72390296</ALEA2>
                                <SITE>Demo-RIPart</SITE>
                            </REPONSE>
                            </geors>
                    """
    xml=XMLResponse(x)
    mess=xml.checkResponseValidity()
    
  
    version= xml.getVersion()
    print version