
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from Client import *
import logging
import RipartLogger
from Croquis import *
from Point import *
from Enum import *


class TestConnection(object):
    '''
    classdocs
    '''
    login = "mborne"
    pwd ="mborne"
    url ="demo-ripart.ign.fr"
    
    
    # create logger
   
    logger=logging.getLogger("ripart.testConnection")
    logger.info("testzzz")
    
    pt= Point(2,40)
 
  
    
    c= Croquis("nom" , Croquis.CroquisType.Ligne)
    
    c.addPoint(pt)
    

    def __init__(self):
        '''
        Constructor
        '''
        self.connect()
        
    def connect(self):
        client = Client(self.url, self.login,self.pwd)
        print client.connect()
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    TestConnection()