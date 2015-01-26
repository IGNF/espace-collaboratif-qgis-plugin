'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''

class Profil(object):
    '''
    classdocs
    '''
    
    
    #Nom de l'auteur   
    auteur=Auteur()
                        
    #Nom du Geogroupe    
    geogroupe= Groupe()
        
    #Titre du Geogroupe   
    titre=""
        
        
    #Statut (privilèges) du profil        
    statut=""
        
    #Lien vers le logo du profil
    logo=""

        
    #Filtre du profil       
    filtre=""
        
    #La zone géographique de travail du profil        
    zone=ZoneGeographique()

        
    #Indique si le profil a acces aux groupes prives
    prive 

        
    #Les éventuels thèmes attachés au profil      
    themes = array(Theme)

        
    #identifiant geoprofil    
    id_Geoprofil=""


    def __init__(self, params):
        '''
        Constructor
        '''
        