# -*- coding: utf-8 -*-
'''
Created on 26 janv. 2015

@author: AChang-Wailing
'''
import logging
import RipartLogger
import xml.etree.ElementTree as ET
from Profil import *
import ConstanteRipart
import sys
import collections
from Remarque import *
from Theme import *
from Point import *
from Auteur import *
from Croquis import *

class XMLResponse(object):
    '''
    classdocs
    '''
    response =""
    
    root=""
    
    logger=logging.getLogger("ripart.XMLResponse")
    
    

    def __init__(self, response):
        '''
        Constructor
        '''
       
        self.response = response;
        
        try:
            self.root =ET.fromstring( self.response)
        except Exception as e:
            self.logger.error(str(e))
         
        
        self.logger.debug("init")
        
        
        
        
    """
        Contrôle la validit� de la r�ponse. 
        Si le code erreur="OK", la r�ponse est valide
        :return: un dictionnaire à 2 cl�s, message et code
    """   
    def checkResponseValidity(self):
       
        errMessage ={'message':'', 'code':''}
        
        try:     
            #self.root =ET.fromstring(self.response)
            erreur= self.root.findall('./REPONSE/ERREUR')
            
            for m in erreur:
                errMessage['message']=m.text
                errMessage['code']=m.attrib['code']
            
        
        except KeyError as e:
            self.logger.error(str(e))
           
        except Exception as e:
            self.logger.error(str(e))
          
            
        return errMessage
   
     
    """
    Extraction des Aleas
    """
    def getAleas(self):
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
    
    
    
    
    """
    Extraction des paramètres de connexion
    :return: un dictionnaire contenant les paramètres de connexion (ID_AUTEUR, JETON, SITE)
    """
    def getConnectValues(self):
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
        
    
    """
    """
    def getCurrentJeton(self):
        
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
                
                
    """
    Extraction du profil à partir de la réponse xml
    :return: profil de l'utilisateur
    """            
    def extractProfil(self):
        profil = Profil()
        
        try:
            node =self.root.find('./PROFIL/ID_GEOPROFIL')  
            profil.id_Geoprofil = node.text
            
            node =self.root.find('./PROFIL/TITRE')
            profil.titre = node.text
            
            node =self.root.find('./PROFIL/ZONE')
            profil.zone = node.text
            
            '''for stat in ConstanteRipart.ZoneGeographique:
                if node.text == str(stat):
                    profil.zone = node.text
                    break'''
            
            gr = Groupe()
            node =self.root.find('./PROFIL/ID_GEOGROUPE')
            gr = node.text
            
            node =self.root.find('./PROFIL/GROUPE')
            gr= node.text
            
            profil.geogroupe= gr
            
            
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
        
        
    """
    Extraction des thèmes associés au profil
    """
    def getThemes(self):
        
        themes=[]
        profil= Profil()
        
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
            raise Exception ("erreur dans la récupération des thèmes")
            
        return themes
    
    
        
    """
    Extraction du nouveau jeton
    :return: le jeton
    """       
    def getCurrentJeton(self):
        jeton =""
        
        try:
            node =self.root.find('./REPONSE/JETON')
            jeton = node.text
        
        except Exception as e:
            self.logger.error('getCurrentJeton:' + str(e) )
            raise Exception ("Jeton non valide")
        
        return jeton
    


    """
    Extraction de la version 
    """
    def getVersion(self):
        v=""
        
        try:
            v=  self.root.attrib['version']
            
        except KeyError as e:
            self.logger.error(str(e))
           
        except Exception as e:
            self.logger.error(str(e)) 
        
        return v
    
    
    """
    Retourne le nombre total de réponses
    :return: nombre total de réponse
    """
    def getTotalResponse(self):
        
        total=0
        try:
            node = self.root.find('PAGE/TOTAL')
            total = node.text
        except Exception as e:
            self.logger.error('getTotalResponse :'+ str(e))
        
        return total
        
        
        
        
    """
    Extraction des remarques de la réponse xml
    :param remarques: la liste de remarques
    :return: la liste de remarques (dans l'ordre inverse d'identifiants)
    """
    def extractRemarques(self,remarques):
        
        dicRem= {}
        
        
        try:
            georems= self.root.findall('GEOREM')
            
            for node in georems :
                
                rem= Remarque()
                themes = []
                
                rem.id= (node.find('ID_GEOREM')).text
                
                rem.autorisation= (node.find('AUTORISATION')).text
                
              
                for th in node.findall('THEME'):                    
                    nomGroupe = (th.find('NOM')).text
                    idGroupe = (th.find('ID_GEOGROUPE')).text
                    
                    theme = Theme()
                    theme.groupe = Groupe(idGroupe, nomGroupe)
                    themes.append(theme)
                    
                rem.themes= themes
                
                
                rem.lien = (node.find('LIEN')).text
                rem.lien.replace("&amp;" , "&");
                
                rem.lienPrive = (node.find('LIEN_PRIVE')).text
                rem.lienPrive.replace("&amp;" , "&");
                
                rem.dateCreation= (node.find('DATE')).text
                
                rem.dateMiseAJour=(node.find('MAJ')).text
                
                rem.dateValidation=(node.find('DATE_VALID')).text
                
                lon =(node.find('LON')).text
                lat= (node.find('LAT')).text
                rem.position = Point(lon,lat)
                
                rem.statut =(node.find('STATUT')).text
                
                rem.departement= Groupe()
                rem.departement.id= (node.find('ID_DEP')).text
                rem.departement.nom =(node.find('DEPARTEMENT')).text
                
                rem.commune= (node.find('COMMUNE')).text
                
                rem.commentaire= (node.find('COMMENTAIRE')).text
                
                rem.auteur = Auteur()
                rem.auteur.id = (node.find('ID_AUTEUR')).text
                rem.auteur.nom =(node.find('AUTEUR')).text
                
                rem.groupe =Groupe()
                rem.groupe.id =(node.find('ID_GEOGROUPE')).text
                rem.groupe.nom =(node.find('GROUPE')).text

                rem.id_partition=(node.find('ID_PARTITION')).text
                
                #croquis
                rem = self.getCroquisForRem(rem, node);
                
                #documents
                
                
                #réponses (GEOREP)
                
                
                rem.hash = (node.find('HASH')).text
                rem.source =(node.find('SOURCE')).text
                
                remarques[rem.id]=rem
                
                
        except Exception as e:
            self.logger.error(str(e))
            
            raise Exception("Une erreur est survenue dans l'importation des remarques")   
                
        
        return remarques
        
        
        
        
    def getCroquisForRem (self , rem, node):
            
        objets= node.findall('CROQUIS/objet')
            
        points = []
            
        for ob in objets:
            croquis = Croquis()
            croquis.type = ob.attrib['type']
            croquis.nom = ob.find('nom').text
            
            
            
            
            #
            rem.AddCroquis(croquis)  
             
             
        #TODO 
            
            
               
        
            
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