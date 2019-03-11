# -*- coding: utf-8 -*-
'''
Created on 2 oct. 2015

version 3.0.0 , 26/11/2018

@author: AChang-Wailing
'''

import logging
import os
from datetime import datetime
import dateutil.relativedelta
import string
import importlib


class RipartLogger(object):
    """Paramètres du log
    """

    logger=None
    logpath=None

    def __init__(self,param=""):
        '''
        Constructor
        '''
           
        #trouve le dossier d'installation du plugin et le nom du fichier de log (yyyymmdd_espaceco.log)
        p = os.path.dirname(__file__)
        lastSlashIdx=p.rfind("\\")
        #lastSlashIdx=string.rfind(os.path.dirname(__file__),"\\")
        logdir= os.path.join(os.path.dirname(__file__)[:lastSlashIdx],"logs")   
            
        today= datetime.now().date().strftime('%Y%m%d')
        logFilename= today+"_espaceco.log"   
        self.logpath=os.path.abspath(os.path.join(logdir,logFilename))
        
                
        if not os.path.exists(logdir):
            os.makedirs(logdir)
                
        if param=="":
            param= "espaceco"
            
        self.logger = logging.getLogger(param)    
                
        self.logger.setLevel(logging.DEBUG)
              
        #if not os.path.exists(self.logpath):
        #    file(self.logpath, 'w').close()
            
        fh = logging.FileHandler(self.logpath)
                
        fh.setLevel(logging.DEBUG)
                
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
                
        # add the handlers to the logger
        self.logger.addHandler(fh)
        
        #supprime les anciens fichiers de log
        self.removeOldLogs(logdir)

   
    def getRipartLogger(self):
        """Retourne le logger
        """
        return self.logger
        
     
    def removeOldLogs(self,logdir):
        """Supprime les fichiers de logs plus vieux qu'un mois
        
        :param logdir: le répertoire des fichiers de log
        :type logdir: string
        """
        today= datetime.now().date()
        lastMonth=today + dateutil.relativedelta.relativedelta(months=-1)

        last=lastMonth.strftime('%Y%m%d')
   
      
        if os.path.exists(logdir):
            for f in os.listdir(logdir):
                if f[ :8] < last:
                    os.remove(os.path.join(logdir,f))
           
           
        
    def getLogpath(self):
        return self.logpath 