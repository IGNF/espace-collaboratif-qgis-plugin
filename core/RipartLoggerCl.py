# -*- coding: utf-8 -*-
'''
Created on 2 oct. 2015

@author: AChang-Wailing
'''
import logging
import os
class RipartLogger(object):
    '''
    classdocs
    '''
    logger=None

    def __init__(self,param=""):
        '''
        Constructor
        '''
        # fonctionne sous windows ou linux
        #par ex: C:\Users\<nom_utlisateur>  ou /home/<nom_utlisateur>
        logdir = os.getenv('HOME') + os.path.sep + "ripart" + os.path.sep 
                
        if not os.path.exists(logdir):
            os.makedirs(logdir)
                
        if param=="":
            param= "ripart"
            
        self.logger = logging.getLogger(param)
                
        self.logger.setLevel(logging.DEBUG)
              
        if not os.path.exists(logdir  + "ripart.log"):
            file(logdir  + "ripart.log", 'w').close()
                
        fh = logging.FileHandler(logdir  + "ripart.log")
                
        fh.setLevel(logging.DEBUG)
                
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
                
        # add the handlers to the logger
        self.logger.addHandler(fh)
        
        


     
    def getRipartLogger(self):
        return self.logger
        
        
        
        