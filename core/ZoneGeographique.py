'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from enum import Enum


class ZoneGeographique(Enum):
    '''
    classdocs
    '''
    UNDEFINED
       
    #France métropolitaine (Corse incluse).
    FXX
    #Terres Articques Australes.
    ATF    
    #Guadeloupe  
    GLP  
    #Guyanne    
    GUF  
    #Martinique  
    MTQ   
    #Mayotte      
    MYT    
    #Nouvelle Caledonie     
    NCL  
    #Polynesie Française   
    PYF    
    #Réunion       
    REU    
    #Saint-Pierre et Miquelon    
    SPM  
    #Wallis et Futuna 
    WLF
    