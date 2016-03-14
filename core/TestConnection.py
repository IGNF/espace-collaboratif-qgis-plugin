# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from Client import *


from Croquis import *
from Point import *
from Enum import *
from RipartLoggerCl import RipartLogger
from RipartServiceRequest import RipartServiceRequest

class TestConnection(object):
    '''
    classdocs
    '''
    login = "achang"
    pwd =""
    url ="https://qlf-collaboratif.ign.fr/collaboratif-site"
    
    
    # create logger
   
    #logger=logging.getLogger("ripart.testConnection")
    logger=RipartLogger("ripart.testConnection").getRipartLogger()
    
    logger.info("testzzz")
    
    pt= Point(2,40)
 
  
    
    c= Croquis("nom" , Croquis.CroquisType.Ligne)
    
    c.addPoint(pt)
    

    def __init__(self):
        '''
        Constructor
        '''
        #self.connect()
        
    def connect(self):
        client = Client(self.url, self.login,self.pwd)
      
        profil= client.getProfil()
        
        params={}
        
        params['updatingDate']=""
        georems= client.getGeoRems()
      
        print "ok"
        
    def postRem(self):
        #client= Client(self.url, self.login,self.pwd)
        
        
        try:
            
            params = {}
          
          
            params['comment']= "test Post georem protocol QGIS"   
                 
            geom= "POINT(2.397 48.844)"
            params['geometry']=geom

            params['territory']= 'FXX'
            
            
            #Ajout des thèmes selectionnés en générant le xml associé
            #themes = '<THEME groupe="BDUni"><ID_GEOGROUPE>1315</ID_GEOGROUPE><NOM>Adresse, Lieux-dits</NOM></THEME>'

            themes = '"3569::Parcelles, Cadastre"=>"1"';
            
            params["attributes"]= themes
                
            params['version']='1_0_0'
            #params['protocol'] ='RIPART_GCEXT_8123'
            params['protocol'] ='RIPART_QGIS_99712'
              
       
            #envoi de la requête
            #data = RipartServiceRequest.makeHttpRequest(self.__url,  data=params, files=files) 
            #data = RipartServiceRequest.makeHttpRequest(self.url,  data=params)     
            
            
            r =  requests.post(self.url +"/api/georem/georem_post.xml", 
                             auth=HTTPBasicAuth(self.login,self.pwd),
                             data=params)   
          
            r.encoding ='utf-8'
            response=r.text
                    
            xmlResponse = XMLResponse(response)
            errMessage= xmlResponse.checkResponseValidity()
            
            if errMessage['code'] =='OK': 
                rems= xmlResponse.extractRemarques()
                if len(rems)==1:
                    rem =rems.values()[0]
                else :
                    self.logger.error("Problème lors de l'ajout de la remarque")
                    raise Exception("Problème lors de l'ajout de la remarque")
            else:
                self.logger.error(errMessage['message'])
                raise Exception(errMessage['message'])
            
            
           
 
            
        except Exception as e:
            self.logger.error(str(e))
            raise Exception(e)
        
       
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    t= TestConnection()
    t.connect()
   # t.postRem()
    