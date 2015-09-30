# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from Enum import Enum

#class ConstanteRipart(object):
'''
constantes
'''
   
#taille maximale pour un document uploadé
MAX_TAILLE_UPLOAD_FILE =  5000000

#nombre par défaut de remarques par page
NB_DEFAULT_REMARQUES_PAGINATION = 100

#Définition du protocole signant au près du service Ripart l'origine de ce programme. 
RIPART_CLIENT_PROTOCOL = "_RIPART_AGIS_64512"

#Définition donnant la version de ce programme.
RIPART_CLIENT_VERSION = "1_0_0"



RIPART_GEOREM_GET = "georem_get";
RIPART_GEOREM_POST = "georem_post";
RIPART_GEOREM_PUT = "georem_put";
RIPART_CONNECT = "connect";
RIPART_GEOAUT_GET = "geoaut_get";
RIPART_QUESTION_POST = "geoquestion_post";
RIPART_QUESTION_GET = "geoquestion_get";


STATUT=  Enum( "undefined","submit","pending", "pending1","pending2","valid","valid0","reject","reject0") 

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
                         #R�union       
                         "REU",    
                         #Saint-Pierre et Miquelon    
                         "SPM",  
                         #Wallis et Futuna 
                         "WLF")
                                
