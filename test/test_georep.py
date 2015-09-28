# -*- coding: utf-8 -*-
'''
Created on 24 sept. 2015

@author: AChang-Wailing
'''

import unittest
import xml.etree.ElementTree as ET
from core.Groupe import Groupe
from core.Auteur import Auteur
from core.GeoReponse import GeoReponse
import core.ConstanteRipart as cr

class Test(unittest.TestCase):

    
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_georep(self):
        rep = GeoReponse()    
        self.assertEquals(rep.statut,cr.STATUT.undefined)
        
        
    def test_encodeToXML(self):
        rep = GeoReponse()
        rep.groupe=Groupe("12","Reponse automatique")
        rep.auteur= Auteur("300","toto")
        rep.statut=cr.STATUT.pending
        rep.reponse="the response..."
        
        date = rep.date.strftime("%Y-%m-%d %H:%M:%S")
        
        xml= rep.encodeToXML()
        sxml= ET.tostring(xml)
        
        expected='<GEOREP>'+ \
        '<ID_GEOREP>12</ID_GEOREP>'+ \
        '<ID_AUTEUR>300</ID_AUTEUR>'+ \
        '<AUTEUR>toto</AUTEUR>'+ \
        '<TITRE>Reponse automatique</TITRE>'+ \
        '<STATUT>pending</STATUT>'+ \
        '<DATE>'+date+'</DATE>'+ \
        '<REPONSE>'+ \
        'the response...'+ \
        '</REPONSE>'+ \
        '</GEOREP>'
        
        self.assertEquals(sxml,expected)