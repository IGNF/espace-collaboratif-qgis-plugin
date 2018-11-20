'''
Created on 1 oct. 2015

@author: AChang-Wailing
'''
#from qgis.utils import *
class RipartException (Exception):
    '''
    classdocs
    '''
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
        