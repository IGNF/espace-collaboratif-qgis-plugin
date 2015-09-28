'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
import unittest
from core.XMLResponse import XMLResponse

class testConnect(unittest.TestCase):

    login = "mborne"
    pwd ="mborne"
    url ="http://demo-ripart.ign.fr"
    
    
  
        
    def testResponseValidity(self):
        x=  """<?xml version='1.0' encoding='UTF-8'?>
                            <geors version='0.1'>
                            <REPONSE type='action=connect'>
                                <ERREUR code='OK'>OK</ERREUR>
                                <ALEA1>6117245975489987c2c8028.02593919</ALEA1>
                                <ALEA2>141784489354899890b49555.72390296</ALEA2>
                                <SITE>Demo-RIPart</SITE>
                            </REPONSE>
                            </geors>
                    """
        xml=XMLResponse(x)
        message= xml.checkResponseValidity()
        self.assertEquals('OK',message['code'])
    
    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()