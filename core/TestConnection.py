'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
import Client

class TestConnection(object):
    '''
    classdocs
    '''
    login = "mborne"
    pwd ="mborne"
    url ="demo-ropart.ign.fr"

    def __init__(self, params):
        '''
        Constructor
        '''
        self.connect()
        
    def connect(self):
        client = Client(url, login, pwd)
        print client.connect()
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    TestConnection()