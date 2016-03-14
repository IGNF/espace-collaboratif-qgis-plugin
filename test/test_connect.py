# -*- coding: utf-8 -*-
'''
Created on 23 janv. 2015

@author: AChang-Wailing
'''
import unittest
from core.XMLResponse import XMLResponse
from core.Client import Client
from core.Box import Box

class testConnect(unittest.TestCase):

    login = "ac"
    pwd ="zzz1801"
    url ="https://qlf-collaboratif.ign.fr"
    
    
  
        
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
    
    
    def test_getRemarqueById(self):
        client = Client(self.url, self.login,self.pwd)
      
        data=client.georem_getById(2603)
        
        xmlresp= XMLResponse(data)
        rems=xmlresp.extractRemarques()
        
        if len(rems) > 0:
            self.assertTrue(rems.has_key('2603'))
        
        
        
        
    def test_getRemarques(self):
        """
        """
        client = Client(self.url, self.login,self.pwd)
        profil= client.getProfil()
        zone = profil.zone
        self.assertEquals(zone.__str__(),"FXX")
        
        #sans bbox
        rems = client.getRemarques(zone, None, 10,"2014-10-01 00:00:00", 8)
                
        self.assertTrue('2603' in rems)
        self.assertTrue(len(rems)>0)
        
    def test_getRemarques2(self):
        """
        """
        client = Client(self.url, self.login,self.pwd)
        profil= client.getProfil()
        zone = profil.zone
        self.assertEquals(zone.__str__(),"FXX")
        
        #sans bbox
        rems = client.getRemarques(zone, None, 100,"2014-11-01 00:00:00", 8)
                
        self.assertTrue('2603' in rems)
        self.assertTrue(len(rems)>0)
        
    def test_getRemarquesBbox(self):
        """
        """
        client = Client(self.url, self.login,self.pwd)
        profil= client.getProfil()
        zone = profil.zone
        
        
        #avec bbox
        box= Box(1.143,46.84,1.9,48.02)
        rems = client.getRemarques(zone, box, 10,"2013-10-01 00:00:00", 8)
                
        self.assertTrue('2325' in rems)
        self.assertTrue(len(rems)>0)
        
    def test_getRemarquesBbox2(self):
        """Avec changement de coordonnées
        """
        client = Client(self.url, self.login,self.pwd)
        profil= client.getProfil()
        zone = profil.zone
        
        
        #avec bbox
        box= Box(1.143,46.84,1.9,48.02)
        rems = client.getRemarques(zone, box, 10,"2013-10-01 00:00:00", 8)
                
        self.assertTrue('2325' in rems)
        self.assertTrue(len(rems)>0)    
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()