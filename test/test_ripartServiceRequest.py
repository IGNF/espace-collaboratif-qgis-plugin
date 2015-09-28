'''
Created on 23 sept. 2015

@author: AChang-Wailing
'''
import unittest

from core.RipartServiceRequest import RipartServiceRequest
from core.XMLResponse import XMLResponse


class TestRipartServiceRequest(unittest.TestCase):

    __login = "acw"
    __pwd ="achang"
    __url ="https://ripart1.ign.fr"
     

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_connection(self):
        rdata =RipartServiceRequest.makeHttpRequest(self.__url, {'action':'connect','login':self.__login})
        #test de connexion (GET)
        #rdata= RipartServiceRequest.makeHttpRequest("http://demo-ripart.ign.fr",params={'action':'connect','login':'mborne'})
        
        print rdata
        self.assertTrue(rdata.startswith('<?xml version'))
        
        #test de connexion (POST)
        rdata= RipartServiceRequest.makeHttpRequest("http://demo-ripart.ign.fr",data={'action':'connect','login':'mborne'})
        
        print rdata
        self.assertTrue(rdata.startswith('<?xml version'))
        
        xmlResponse = XMLResponse(rdata)
            
        errMessage = xmlResponse.checkResponseValidity()
        
        self.assertEquals(errMessage['code'],"OK")
        


if __name__ == "__main__":
    
    unittest.main()