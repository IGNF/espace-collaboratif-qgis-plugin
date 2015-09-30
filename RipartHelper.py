# -*- coding: utf-8 -*-
'''
Created on 29 sept. 2015

@author: AChang-Wailing
'''
import logging
import core.RipartLogger 
import xml.etree.ElementTree as ET

class RipartHelper(object):
    """"
    Classe contenant des utilitaires pour le plugin
    """
    
    nom_Fichier_Ripart = "Ripart.gdb";
    nom_Fichier_Parametres_Ripart = "Ripart.xml";

    nom_Calque_Remarque = "Remarque_Ripart";
    nom_Calque_Croquis_Fleche = "Croquis_Ripart_Fleche";
    nom_Calque_Croquis_Texte = "Croquis_Ripart_Texte";
    nom_Calque_Croquis_Polygone = "Croquis_Ripart_Polygone";
    nom_Calque_Croquis_Ligne = "Croquis_Ripart_Ligne";
    nom_Calque_Croquis_Point = "Croquis_Ripart_Point";

    calque_Remarque_Lyr = "Remarque_Ripart.lyr";

    nom_Champ_IdRemarque = u"N°remarque";
    nom_Champ_Auteur = "Auteur";
    nom_Champ_Commune = "Commune";
    nom_Champ_Departement = u"Département";
    nom_Champ_IDDepartement = "Département_ID";
    nom_Champ_DateCreation = "Date_de_création";
    nom_Champ_DateMAJ = "Date_MAJ";
    nom_Champ_DateValidation = "Date_de_validation";
    nom_Champ_Themes = "Thèmes";
    nom_Champ_Statut = "Statut";
    nom_Champ_Message = "Message";
    nom_Champ_Reponse = "Réponses";
    nom_Champ_Url = "URL";
    nom_Champ_UrlPrive = "URL_privé";
    nom_Champ_Document = "Document";
    nom_Champ_Autorisation = "Autorisation";

    nom_Champ_LienRemarque = "Lien_remarque";
    nom_Champ_NomCroquis = "Nom";
    nom_Champ_Attributs = "Attributs_croquis";
    nom_Champ_LienBDuni = "Lien_object_BDUni";

    xml_UrlHost = "./Serveur/URLHost";
    xml_Login = "./Serveur/Login";
    xml_DateExtraction = "./ArcMap/Date_extraction";
    xml_Pagination = "/Paramètres_connexion_à_Ripart/ArcMap/Pagination";
    xml_Themes = "/Paramètres_connexion_à_Ripart/ArcMap/Thèmes_préférés/Thème";
    xml_Zone_extraction = "/Paramètres_connexion_à_Ripart/ArcMap/Zone_extraction";
    xml_AfficherCroquis = "/Paramètres_connexion_à_Ripart/ArcMap/Afficher_Croquis";
    xml_AttributsCroquis = "/Paramètres_connexion_à_Ripart/ArcMap/Attributs_croquis";
    xml_BaliseNomCalque = "Calque_Nom";
    xml_BaliseChampCalque = "Calque_Champ";
    xml_Group = "/Paramètres_connexion_à_Ripart/ArcMap/Import_pour_groupe";

    url_Manuel = "C:\\Ripart\\Manuel d'utilisation de l'add-in RIPart pour ArcMap.pdf"; 

    dateDefaut = "01/01/1900";
    longueurMaxChamp = 5000;
    
    
    #xmlroot=""
       
    logger=logging.getLogger("RipartHelper")
    

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
        