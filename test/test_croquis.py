# -*- coding: utf-8 -*-
'''
Created on 23 sept. 2015

@author: AChang-Wailing
'''
import unittest
import xml.etree.ElementTree as ET
from core.Croquis import Croquis 
from core.Point import Point
from core.Attribut import Attribut
from core.XMLResponse import XMLResponse
from core.Remarque import Remarque

class Test(unittest.TestCase):

    xml="""<CROQUIS xmlns:gml="http://www.opengis.net/gml">
 <objet type="Ligne">
  <nom></nom>
  <geometrie>
   <gml:LineString>
    <gml:coordinates>-1.5796599735262775,46.416677052441457 -1.5793006602337949,46.417212825275676 -1.579064584433467,46.417476660881178 -1.5786314226107703,46.417583345622631</gml:coordinates>
   </gml:LineString>
  </geometrie>
  <attributs>
   <attribut name="Type GéoConcept">toto</attribut>
   <attribut name="Sous-type GéoConcept">toto</attribut>
  </attributs>
 </objet>
</CROQUIS>
"""
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_croquis(self):
        cr= Croquis()
        cr.nom ="my croquis"
        
        self.assertTrue(cr!=None, "Croquis not created")
    
    def test_addpoint(self):
        cr= Croquis()
        cr.nom ="my croquis"
        pt= Point(2,3)
        cr.addPoint(pt)
        
        self.assertTrue(len(cr.points)==1)
        self.assertTrue(cr.type==cr.CroquisType.Vide)
        self.assertFalse(cr.isValid())
        
        cr.type= cr.CroquisType.Point
        self.assertTrue(cr.isValid(),"Is a valid point")
  
        cr.addPoint(Point(3,4))
        cr.type=cr.CroquisType.Polygone
        self.assertFalse(cr.isValid(), "not a valid polygon")
        

        cr.addPoint(Point(5,10))
        cr.addPoint(Point(2,3))
        self.assertTrue(cr.isValid(), "is a valid polygon")
        
    def test_encodeToXML(self):
        cr = Croquis()
        cr.nom= "my croquis"
        gmlurl="http://www.opengis.net/gml"
        doc = ET.Element("CROQUIS",{"xmlns:gml":gmlurl})
        xml=cr.encodeToXML(doc)
        sxml=ET.tostring(xml)
        self.assertEquals(sxml, '<CROQUIS xmlns:gml="http://www.opengis.net/gml" />')
        
        cr.type=cr.CroquisType.Point
        cr.addPoint(Point(1,2))
        xml=cr.encodeToXML(doc)
        sxml=ET.tostring(xml)
        
        expected='<CROQUIS xmlns:gml="http://www.opengis.net/gml">'+ \
        '<objet type="Point">'+  \
        '<nom>'+cr.nom+'</nom>' + \
        '<geometrie>'+  \
        '<gml:Point>'+  \
        '<gml:coordinates>1,2 </gml:coordinates>'+  \
        '</gml:Point>'+  \
        '</geometrie>'+  \
        '<attributs />'+  \
        '</objet>'+  \
        '</CROQUIS>'

        self.assertEquals(sxml, expected)
        
        self.assertTrue(cr.getPoint(0).eq(Point(1,2)))
        self.assertTrue(cr.firstCoord().eq(Point(1,2)))
        self.assertTrue(cr.lastCoord().eq(Point(1,2)))
        
        cr.type=cr.CroquisType.Ligne
        cr.addPoint(Point(3,4))
        cr.addPoint(Point(4,1))
        doc = ET.Element("CROQUIS",{"xmlns:gml":gmlurl})
        xml=cr.encodeToXML(doc)
        sxml=ET.tostring(xml)
        
        expected='<CROQUIS xmlns:gml="http://www.opengis.net/gml">'+ \
        '<objet type="Ligne">'+  \
        '<nom>'+cr.nom+'</nom>' + \
        '<geometrie>'+  \
        '<gml:LineString>'+  \
        '<gml:coordinates>1,2 3,4 4,1 </gml:coordinates>'+  \
        '</gml:LineString>'+  \
        '</geometrie>'+  \
        '<attributs />'+  \
        '</objet>'+  \
        '</CROQUIS>'
        
        
        cr.type=cr.CroquisType.Polygone
        cr.addPoint(Point(1,2))
        cr.addAttribut(Attribut("comment","un triangle"))
        cr.addAttribut(Attribut("date","24/09/2015"))
        
        doc = ET.Element("CROQUIS",{"xmlns:gml":gmlurl})
        xml=cr.encodeToXML(doc)
        sxml=ET.tostring(xml)
        
        expected='<CROQUIS xmlns:gml="http://www.opengis.net/gml">'+ \
        '<objet type="Polygone">'+  \
        '<nom>'+cr.nom+'</nom>' + \
        '<geometrie>'+  \
        '<gml:Polygon>'+  \
        '<gml:outerBoundaryIs>'+  \
        '<gml:LinearRing>'+  \
        '<gml:coordinates>1,2 3,4 4,1 1,2 </gml:coordinates>'+  \
        '</gml:LinearRing>'+  \
        '</gml:outerBoundaryIs>'+  \
        '</gml:Polygon>'+  \
        '</geometrie>'+  \
        '<attributs>'+  \
        '<attribut name="comment">un triangle</attribut>'+  \
        '<attribut name="date">24/09/2015</attribut>'+  \
        '</attributs>'+  \
        '</objet>'+  \
        '</CROQUIS>'


    """def test_geometry(self):
        xmlresponse= XMLResponse(self.xml)
        rem= Remarque()
        
        xmlresponse.getCroquisForRem(rem, node)
    """
    
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()