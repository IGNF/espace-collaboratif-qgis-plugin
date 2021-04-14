# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015
Updated on 15 dec. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse
'''

from .Enum import Enum


'''
constantes
'''
   
#taille maximale pour un document uploadé
MAX_TAILLE_UPLOAD_FILE = 16000000

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


STATUT=  Enum( "undefined","submit","pending","pending0", "pending1","valid","valid0","reject","reject0","pending2") 

openStatut = [STATUT.undefined.__str__(),STATUT.submit.__str__(),STATUT.pending.__str__(),STATUT.pending0.__str__(),
               STATUT.pending1.__str__(),STATUT.pending2.__str__()]

statutLibelle=[u"Reçu dans nos services",
               u"En cours de traitement",
               u"Demande de qualification",
               u"En attente de saisie",  
               u"Pris en compte",
               u"Déjà pris en compte",
               u"Rejeté (hors spec.)",
               u"Rejeté (hors propos)",
               u"En attente de validation"]



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

helpFile="Manuel utilisateur plugin Espace Collaboratif pour QGIS.pdf"    



def statuts():
    statuts=[STATUT.submit.__str__(),
             STATUT.pending.__str__(),
             STATUT.pending0.__str__(),
             STATUT.pending1.__str__(),
             STATUT.valid.__str__(),
             STATUT.valid0.__str__(),
             STATUT.reject.__str__(),
             STATUT.reject0.__str__(),
             STATUT.pending2.__str__()
             ]
    return statuts

# Constantes pour le chargement des couches du guichet
# Types de couches, balise <TYPE>
WMS = "WMS"
WFS = "WFS"
WMTS = "WMTS"
WCS = "WCS"
GEOPORTAIL = "GeoPortail"
COLLABORATIF = "collaboratif.ign.fr"
WXSIGN = "wxs.ign.fr"
DEMO = "Démonstration"
CLEGEOPORTAILSTANDARD = "choisirgeoportail"

