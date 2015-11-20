
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
from Client import *


from Croquis import *
from Point import *
from Enum import *
from RipartLoggerCl import RipartLogger

class TestConnection(object):
    '''
    classdocs
    '''
    login = "mborne"
    pwd ="mborne"
    url ="http://zdemo-ripart.ign.fr"
    
    
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
        #print client.connect()
        profil= client.getProfil()
        #profil= Profil()
        print "ok"

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    t= TestConnection()
    t.connect()
    