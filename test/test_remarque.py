# -*- coding: utf-8 -*-
'''
Created on 23 sept. 2015

@author: AChang-Wailing
'''
import unittest

from core.Remarque import Remarque
from core.Theme import Theme
from core.Groupe import Groupe
from core.GeoReponse import GeoReponse
from core.Auteur import Auteur
from core.Croquis import Croquis 
from core.Point import Point
import core.ConstanteRipart as cst
from datetime import  datetime
import copy
from Contexte import Contexte
#import xml.etree.cElementTree as et

class TestRemarque(unittest.TestCase):

    rem= None
    
    def setUp(self):
        """
        Création d'un objet Remarque
        """
        unittest.TestCase.setUp(self)
        self.rem = Remarque()
        
        
    def test_createRemarque(self): 
        """Test si l'objet est bien créé"""
        
        self.assertTrue(self.rem!=None)
        
        
    def test_addTheme(self):
        """Ajout de thèmes,concaténation des noms des thèmes"""
        
        th =Theme()
        th.groupe= Groupe("10","themaA")
        self.rem.addTheme(th)
        th2= Theme()
        th2.groupe= Groupe("11","themaB")
        self.rem.addTheme(th2)
        
        themes= self.rem.concatenateThemes()
        
        self.assertEquals(themes, "themaAthemaB","concatenateThemes incorrect")
        

    def test_addThemeList(self):
        """Ajout d'une liste de thèmes"""
        
        th =Theme()
        th.groupe= Groupe("10","themaA")
        th2= Theme()
        th2.groupe= Groupe("11","themaB")
        thList=[th,th2,th]
        
        self.rem.clearThemes()
        self.assertTrue(len(self.rem.themes)==0)
        
        self.rem.addThemeList(thList)
        self.assertEquals(len(self.rem.themes), 3, "Problem in addThemeList")
        
        
 
    def test_addGeoReponse(self):
        geoRep= GeoReponse()
        auteur=Auteur(354,"toto")
        geoRep.auteur= auteur   
        
        group=Groupe("10","My response")
        geoRep.groupe= group
       
        geoRep.statut= cst.STATUT.pending
        geoRep.reponse="blabla"
        
        xml=geoRep.encodeToXML()
        
        self.assertEquals(xml.findtext('AUTEUR'),"toto","auteur incorrect")
        
        self.assertTrue(geoRep!=None)
        self.assertEquals(geoRep.titre(),"My response","GeoReponse title incorrect")
        
        self.rem.addGeoReponse(geoRep)
        
        self.assertTrue(len(self.rem.reponses)==1)
        
        geoRep2= copy.copy(geoRep)
        geoRep2.date=datetime.now()
        geoRep2.reponse="blabla2 zz"
        self.rem.addGeoReponse(geoRep2)
        
        self.assertTrue(len(self.rem.reponses)==2)
        
        self.assertEquals(self.rem.reponses[0].reponse,"blabla")
        self.assertEquals(self.rem.reponses[1].reponse,"blabla2 zz")
        
        #print "Test concatenateReponse: \n"
        rep=self.rem.concatenateReponse()
        self.assertTrue(rep.endswith('blabla2 zz\n'))
        s=u"Réponse n°2"
        self.assertTrue(rep.decode('utf-8').startswith(s))  
           

        #print "Test concatenateReponseHTML: \n"
        repHtml=self.rem.concatenateReponseHTML()
        self.assertTrue(repHtml.endswith('<br>blabla2 zz</li><br><br>'))
        
       
        
        
        
    def test_addDocuments(self):
        self.rem.addDocument("document1")
        
        self.assertTrue(len(self.rem.documents)==1)
        
        docs=["doc2","doc3"]
        self.rem.addDocumentList(docs)
        
        self.assertTrue(len(self.rem.documents)==3)
        
        #self.assertEquals(self.rem.documents[0], "document1")
        
        #self.assertEquals(self.rem.getFirstDocument(), "document1", "getFirstDocument !=document1")
        
        
    def test_addCroquis(self):
        croquis= Croquis("my croquis",None,Point(10,22))
        croquis.type=croquis.CroquisType.Point
        
        self.rem.addCroquis(croquis)
        
        self.assertTrue(len(self.rem.croquis)==1)
        self.assertEquals(self.rem.croquis[0].nom,"my croquis")
        
        croquis2= copy.copy(croquis)
        croquis2.nom="2nd croquis"
        croquis2.type= croquis2.CroquisType.Ligne
        
        self.rem.addCroquisList([croquis,croquis2])
        self.assertTrue(len(self.rem.croquis)==3)
        
        self.assertEquals(self.rem.croquis[2].type,croquis2.CroquisType.Ligne,"Le type n'est pas une ligne")
        
        isCroquisEmpty=self.rem.isCroquisEmpty()
        
        self.assertEquals(isCroquisEmpty,False,"No croquis found, but rem has croquis")
                                 
        
    def test_croquis(self):

        isCroquisEmpty=self.rem.isCroquisEmpty()
        
        self.assertEquals(isCroquisEmpty,True,"No croquis in rem, but croquis found")
        
    """def test_updateRemarque(self):
        rem = Remarque()
        rem.id=2871
        rem.dateMiseAJour = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        rem.dateValidation = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        
        context= Contexte.getInstance(None, None)
    """
if __name__ == "__main__":
   
    unittest.main()