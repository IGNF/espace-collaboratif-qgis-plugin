# -*- coding: utf-8 -*-
"""
Created on 23 janv. 2015

@author: AChang-Wailing
"""

from Point import Point
import ConstanteRipart
from  Groupe import Groupe
from Auteur import Auteur
from Theme  import Theme
from datetime import datetime
from ClientHelper import ClientHelper

class Remarque(object):
    """
    Classe représentant une remarque
    """
    
    #Identifiant de la remarque
    id = None  
    
    # Url vers la remarque sur le site  web  publicde Ripart
    lien =""
    
    #Url vers la partie privée du site web de Ripart
    lienPrive=""
    
    # date de création de la remarque Ripart
    dateCreation = datetime.now()
    
    # date de mise-à-jour de la remarque Ripart
    dateMiseAJour = datetime.now()
    
    #date de validation de la remarque Ripart
    dateValidation = None
    
    #position de la remarque ripart (lon/lat)
    position = Point()
    
    #statut de la remarque
    statut= ConstanteRipart.STATUT.undefined
    
    # Le département où est située la remarque (indicatif + nom)
    departement=Groupe()
    
    #commune de la remarque
    commune=""
    
    #texte de la remarque
    commentaire=""
    
    #auteur de la remarque
    auteur = Auteur()
    
    
    #Définit les droits d'action de l'utilisateur en cours sur la remarque Ripart
    autorisation=""
 
    #
    id_partition=""
    
    # groupe sous lequel l'auteur a crée la remarque Ripart 
    groupe= Groupe()
    
    # réponses de la remarque Ripart (liste d'objet GeoReponse)
    reponses = []
    
    # croquis de la remarque  list(Croquis)
    croquis = []
    
    
    #documents attachés à la remarque  (liste de string)
    documents= []
    
    
    # thèmes attachés à la remarque  list(Theme)
    themes = []
    
    #
    hash= ""
    
    source=""
    

    def __init__(self):
        """Constructor
        """
        self.id = None  
        self.lien =""
        self.lienPrive=""
        self.dateCreation = datetime.now()
        self.dateMiseAJour = datetime.now()
        self.dateValidation = None
        self.position = Point()
        self.statut= ConstanteRipart.STATUT.undefined
        self.departement=Groupe()
        self.commune=""
        self.commentaire=""
        self.auteur = Auteur()
        self.autorisation=""
        self.id_partition=""
        self.groupe= Groupe()
        self.reponses = []
        self.croquis = []
        self.documents= []
        self.themes = []
        self.hash= ""
        self.source=""
        
    
    def getAttribut(self,attName, subAtt=None):
        att= getattr(self, attName)
        if att==None:
            return ""
        elif subAtt!=None:       
            return ClientHelper.getValForDB(getattr(att,subAtt))
        else:
            return ClientHelper.getValForDB(att)   

        
    def concatenateThemes(self):
        """Concatène les noms de tous les thèmes de la remarque
        
        :return:  concaténation des noms de tous les thèmes de la remarque 
        :rtype: string
        """
        result=""
        
        for t in self.themes:
            if isinstance(t, Theme):           
                result += ClientHelper.getValForDB(t.groupe.nom)+"|"
                
        return result[:-1]         
                
                
    def isCroquisEmpty(self):
        """True s'il n'y a pas de croquis associé à la remarque. False dans le cas contraire.
        """
        return len(self.croquis) == 0
     
     
    def getAuteurNom(self):
        """Retourne le  nom de l'auteur de la remarque
        """
        return self.auteur.nom
                
     
    def getAuteurId(self):
        """Retourne l'id de l'auteur de la remarque
        """
        return self.auteur.id
     
     
    def getLongitude(self):
        """Retourne la longitude 
        """
        return self.position.longitude
    
         
    def getLatitude(self):
        """Retourne la latitude
        """
        return self.position.latitude
    
         
    def getFirstDocument(self):
        """Retourne le premier document attaché à la remarque (s'il y en a un)
        """
        if len(self.documents)==0 :
            return ""
        else :
            return self.documents[0].text
         
    
    
    def concatenateReponseHTML(self):
        """Crée et retourne la réponse au format html, à partir des réponses existantes pour la remarque
        """
        concatenate=""
        
        if (len(self.reponses) ==0):
            concatenate +=  "<font color=\"red\">Pas de réponse actuellement pour la remarque n°" + self.id.__str__() + ".</font>"
        else : 
            count= len(self.reponses)
            for rep in self.reponses:
                concatenate +="<li><b><font color=\"green\">Réponse n°" + count.__str__();
                count -=1
                
                if len(rep.auteur.nom)!=0 : 
                    concatenate +=" par " + ClientHelper.stringToStringType(rep.auteur.nom)
                if rep.date is not None:
                    concatenate += " le " + rep.date.strftime("%Y-%m-%d %H:%M:%S")
                
                concatenate += ".</font></b><br/>" + ClientHelper.stringToStringType(rep.reponse.strip().replace("\n","<br/>")) + "</li>";
            
        return concatenate
    
    
    def concatenateReponse(self):
        """Crée et retourne la réponse à partir des réponses existantes pour la remarque
        """
        concatenate=""
        
        if (len(self.reponses) ==0):
            concatenate +=   "Pas de réponse actuellement pour la remarque n°"+ self.id.__str__() + "."
        else : 
            count= len(self.reponses)
            for rep in self.reponses:
                concatenate +="Réponse n°" + count.__str__();
                count -=1
                
                if len(rep.auteur.nom)!=0 : 
                    concatenate +=" par " +  ClientHelper.stringToStringType(rep.auteur.nom)
                if rep.date is not None:
                    concatenate += " le " + rep.date.strftime("%Y-%m-%d %H:%M:%S")
                
                concatenate += ".\n" + ClientHelper.stringToStringType(rep.reponse.strip()) + "\n";
            
        return concatenate
    
    
    # obsolète ??    
    #def reponsesEncodeToXML(self):
    #    """
    #     Retourne les GeoReponse de la Remarque sous forme d'un XML
    #    """
        
    def setPosition(self, position):
        """ Set de la position de la remarque
        
        :param position la position de la remarque  (point)
        :type Point
        """
        self.position = position   
          
        
    def setCommentaire(self,commentaire):  
        """Set du commentaire
        
        :param commentaire le commentaire (message) de la remarque
        :type string
        """
        self.commentaire = commentaire
        
        
    def addDocument(self, document):
        """Ajoute un document à la remarque
        
        :param document : le document à ajouter à la remarque
        :type document : string
        """
        self.documents.append(document)
        
  
    #TODO voir si utile ???
    def addDocumentList(self, docList):
        """Ajoute une liste de documents à la remarque
        
        :param docList : une liste de documents
        :type docList: list (of string)
        """
        self.documents.extend(docList)
       
         
   
    def addCroquis(self, croquis):
        """ Ajoute un croquis à la liste de croquis de la remarque
        
        :param croquis: le croquis 
        :type croquis: Croquis
        """
        self.croquis.append(croquis)
       

    
    def addCroquisList(self, listCroquis):
        """Ajoute une liste de croquis à la liste de croquis de la remarque
         
         :param listCroquis: la liste de croquis 
         :type listCroquis: list (de Croquis)
        """      
        self.croquis.extend(listCroquis)
        
        
    def clearCroquis(self):
        """ Supprime tous les croquis de la liste"""      
        self.croquis=[]
        
   
    def addGeoReponse(self, reponse):
        """Ajoute une réponse à la remarque
          
        :param reponse: la réponse
        :type reponse: GeoReponse
        """
        self.reponses.append(reponse)
    
    
    def addTheme(self,theme):
        """Ajoute un thème
        
        :param theme: un Theme
        :type theme : Theme
        """       
        self.themes.append(theme)
        
        
    def addThemeList(self,listThemes):
        """Ajoute une liste de thèmes
        
        :param listThemes: la liste de thèmes
        :type listThemes : list (de Theme)
        """
        self.themes.extend(listThemes)
        
        
    def clearThemes(self):
        self.themes= []
        
    
    
             
                
                

        