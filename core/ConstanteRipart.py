# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from Enum import Enum


'''
constantes
'''
   
#taille maximale pour un document uploadé
MAX_TAILLE_UPLOAD_FILE =  5000000

#nombre par défaut de remarques par page
NB_DEFAULT_REMARQUES_PAGINATION = 100

#Définition du protocole signant au près du service Ripart l'origine de ce programme. 
RIPART_CLIENT_PROTOCOL = "_RIPART_QGIS_99712"


#Définition donnant la version de ce programme.
RIPART_CLIENT_VERSION = ""



RIPART_GEOREM_GET = "georem_get";
RIPART_GEOREM_POST = "georem_post";
RIPART_GEOREM_PUT = "georem_put";
RIPART_CONNECT = "connect";
RIPART_GEOAUT_GET = "geoaut_get";
RIPART_QUESTION_POST = "geoquestion_post";
RIPART_QUESTION_GET = "geoquestion_get";


STATUT=  Enum( "undefined","submit","pending","pending0", "pending1","pending2","valid","valid0","reject","reject0") 

openStatut = [STATUT.undefined.__str__(),STATUT.submit.__str__(),STATUT.pending.__str__(),STATUT.pending0.__str__(),
               STATUT.pending1.__str__(),STATUT.pending2.__str__()]

statutLibelle=[u"Reçue dans nos services",
               u"En cours de traitement",
               u"Demande de qualification",
               u"En attente de saisie",
               u"En attente de validation",
               u"Prise en compte",
               u"Déjà prise en compte",
               u"Rejetée (hors spec.)",
               u"Rejetée (hors propos)"]



ZoneGeographique = Enum ("UNDEFINED",
                         #France métropolitaine (Corse incluse).
                         "FXX",
                         #Terres Articques Australes.
                         "ATF"  , 
                         #Guadeloupe  
                         "GLP",  
                         #Guyanne    
                         "GUF",  
                         #Martinique  
                         "MTQ",   
                         #Mayotte      
                         "MYT",    
                         #Nouvelle Caledonie     
                         "NCL",  
                         #Polynesie Française   
                         "PYF",    
                         #Réunion       
                         "REU",    
                         #Saint-Pierre et Miquelon    
                         "SPM",  
                         #Wallis et Futuna 
                         "WLF")

namespace={'gml':'http://www.opengis.net/gml'}      

helpFile="Manuel utilisateur plugin RIPart pour QGIS.pdf"    



def statuts():
    statuts=[STATUT.submit.__str__(),
             STATUT.pending.__str__(),
             STATUT.pending0.__str__(),
             STATUT.pending1.__str__(),
             STATUT.pending2.__str__(),
             STATUT.valid.__str__(),
             STATUT.valid0.__str__(),
             STATUT.reject.__str__(),
             STATUT.reject0.__str__()
             ]
    return statuts
    
