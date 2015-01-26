'''
Created on 26 janv. 2015

@author: AChang-Wailing
'''
import logging
import os

class RipartLogger(object):
    '''
    classdocs
    '''
    # fonctionne sous windows ou linux
    #par ex: C:\Users\<nom_utlisateur>  ou /home/<nom_utlisateur>
    logdir = os.getenv('HOME')
    
    logger = logging.getLogger("ripart_plugin")
    
    logger.setLevel(logging.DEBUG)
  
    fh = logging.FileHandler('spam.log')