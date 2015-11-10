'''
Created on 10 nov. 2015

@author: AChang-Wailing
'''

class Magicwand(object):
    '''
    classdocs
    '''
    
    context=None

    def __init__(self, context):
        '''
        Constructor
        '''
        self.context=context
     
    def selectRipartObjects(self):
        self.context.getSelectedRipartFeatures()
        pass
     
    
    def selectCroquisForRemark(self):
        print("croquis")
        
    
    def selectRemarkForCroquis(self):
        pass