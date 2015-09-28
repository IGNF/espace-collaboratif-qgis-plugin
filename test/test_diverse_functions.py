'''
Created on 24 sept. 2015

@author: AChang-Wailing
'''
import unittest
import core.ConstanteRipart as cst
from core.Remarque import Remarque


class TestDiverseFunctions(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    
    def test_enum(self):
        """Test EMUN
        """
        rem = Remarque()
        statut = cst.STATUT.pending
        rem.statut = statut      
        
        statutStr="valid"
        
        rem.statut = cst.STATUT.__getitemFromString__(statutStr)
        
        self.assertEquals(rem.statut, cst.STATUT.valid, "False statut found in enum")
 

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()