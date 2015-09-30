# -*- coding: utf-8 -*-
'''
Created on 24 sept. 2015

@author: AChang-Wailing
'''
import unittest

from core.XMLResponse import XMLResponse

class TestXmlResponse(unittest.TestCase):

    xml1= """<?xml version='1.0' encoding='UTF-8'?>
<geors version='0.1'>
<REPONSE type='connect'>
    <ERREUR code='OK'>OK</ERREUR>
    <ALEA1>484376529560287b9419a75.70279673</ALEA1>
    <ALEA2>286485418560291c537f0a9.13606656</ALEA2>
    <SITE>Demo-RIPart</SITE>
</REPONSE>
</geors>"""

    xmlAleas="""<?xml version='1.0' encoding='UTF-8'?>
<geors version='0.1'>
<REPONSE type='connect'>
    <ERREUR code='OK'>OK</ERREUR>
    <ALEA1>50477801556023f1894d172.93762979</ALEA1>
    <ALEA2>484376529560287b9419a75.70279673</ALEA2>
    <SITE>Demo-RIPart</SITE>
</REPONSE>
</geors>"""

    xmlConnectValues="""<?xml version='1.0' encoding='UTF-8'?>
<geors version='0.1'>
<REPONSE type=''>
    <ERREUR code='OK'>OK</ERREUR>
    <ID_AUTEUR>354</ID_AUTEUR>
    <JETON>102814614056091cbf5b4104.13262433</JETON>
    <SITE>Demo-RIPart</SITE>
</REPONSE>
</geors>"""

    xmlAut="""<?xml version='1.0' encoding='UTF-8'?>
<geors version='0.1'>
<REPONSE type='geoaut_get'>
    <ERREUR code='OK'>OK</ERREUR>
    <JETON>152628375956091cbf658ff2.15839337</JETON>
    <SITE>Demo-RIPart</SITE>
</REPONSE>
<AUTEUR>
        <NOM>mborne</NOM>
        <STATUT>1comite</STATUT>
        <STATUTXT>R dacteur</STATUTXT>
    </AUTEUR>
    <PROFIL>
        <ID_GEOPROFIL>277</ID_GEOPROFIL>
        <TITRE>profil éèà</TITRE>
        <ZONE>FXX</ZONE>
        <ID_GEOGROUPE>8</ID_GEOGROUPE>
        <GROUPE>Groupe Test</GROUPE>
        <LOGO>http://demo-ripart.ign.fr/IMG/rubon8.jpg</LOGO>
        <FILTRE></FILTRE>
        <PRIVE>0</PRIVE>
    </PROFIL>
    <THEMES>   
         <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Route</NOM>
        </THEME>
    
         <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Adresse, Lieux-dits</NOM>
        </THEME>
    
         <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Points d'intérêt</NOM>
        </THEME>
    
         <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Bâti</NOM>
        </THEME>
    
         <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Administratif</NOM>
        </THEME>
         <THEME>
            <ID_GEOGROUPE>21</ID_GEOGROUPE> 
            <NOM>Sentier, GR</NOM>
        </THEME>
    
         <THEME>
            <ID_GEOGROUPE>21</ID_GEOGROUPE> 
            <NOM>Parcelles, Cadastre</NOM>
        </THEME>
    
         <THEME>
            <ID_GEOGROUPE>21</ID_GEOGROUPE> 
            <NOM>Autre</NOM>
        </THEME>
        <THEME>
            <ID_GEOGROUPE>11</ID_GEOGROUPE> 
            <NOM>@BDCarthage</NOM>
        </THEME>
         <THEME>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Voeux</NOM>
        </THEME>
    
        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Voeux</NOM>
            <ATT>Type</ATT>
            <TYPE>list</TYPE>
            <VALEURS>&lt;VAL&gt;&lt;/VAL&gt;&lt;VAL&gt;Santé&lt;/VAL&gt;&lt;VAL&gt;Joie&lt;/VAL&gt;&lt;VAL&gt;Amour&lt;/VAL&gt;&lt;VAL&gt;Bonheur&lt;/VAL&gt;&lt;VAL&gt;Sérénité&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>   
         <THEME>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
        </THEME>
    
        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
            <ATT>Type de voie</ATT>
            <TYPE>text</TYPE>
            <VALEURS>&lt;VAL&gt;&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>  
        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
            <ATT>Type 2</ATT>
            <TYPE>list</TYPE>
            <VALEURS>&lt;VAL&gt;&lt;/VAL&gt;&lt;VAL&gt;autoroute&lt;/VAL&gt;&lt;VAL&gt;route principale&lt;/VAL&gt;&lt;VAL&gt;route secondaire&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>   
        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
            <ATT>type 3</ATT>
            <TYPE>checkbox</TYPE>
            <VALEURS>&lt;VAL&gt;nature&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>
    
        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
            <ATT>toto</ATT>
            <TYPE>list</TYPE>
            <VALEURS>&lt;VAL&gt;toto&lt;/VAL&gt;&lt;VAL&gt;titi&lt;/VAL&gt;&lt;VAL&gt;tutu&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>
    
         <THEME>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Défense</NOM>
        </THEME>
    </THEMES>
    <GEOGROUPE>
        <ID_GEOGROUPE>8</ID_GEOGROUPE>
        <NOM>Groupe Test</NOM>
        <ADMIN></ADMIN>
    </GEOGROUPE>
    <GEOGROUPE>
        <ID_GEOGROUPE>50</ID_GEOGROUPE>
        <NOM>ICPE</NOM>
        <ADMIN></ADMIN>
    </GEOGROUPE>
</geors>"""

    xmlRem ="""<?xml version='1.0' encoding='UTF-8'?>
<geors version='0.1'>
<REPONSE type='georem_get'>
    <ERREUR code='OK'>OK</ERREUR>
    <JETON>1889308810560938f445ae69.70222259</JETON>
    <SITE>Demo-RIPart</SITE>
</REPONSE>

<PAGE>
    <POSITION>1</POSITION>
    <TOTAL>1</TOTAL>
    <DATE>2015-09-28 14:09:20</DATE>
</PAGE>

<GEOREM>
    <ID_GEOREM>2612</ID_GEOREM>
    <SELECT>1</SELECT>
    <AUTORISATION>RW-</AUTORISATION>
    <HASH>492021be30</HASH>
    <THEME groupe='BDUni'>
        <ID_GEOGROUPE>7</ID_GEOGROUPE>
        <NOM>Bâti</NOM>
    </THEME>
    <THEME groupe='IGN'>
        <ID_GEOGROUPE>21</ID_GEOGROUPE>
        <NOM>Autre</NOM>
    </THEME>
    <THEME groupe='Groupe Test'>
        <ID_GEOGROUPE>8</ID_GEOGROUPE>
        <NOM>Voeux</NOM>
    </THEME>

    <LIEN>http://demo-ripart.ign.fr/?page=geo_list&amp;id_georem=2612</LIEN>
    <LIEN_PRIVE>http://demo-ripart.ign.fr/ecrire/?exec=georem_admin&amp;id_georem=2612</LIEN_PRIVE>
    <DATE>2014-12-01 17:22:27</DATE>
    <MAJ>2014-12-03 16:42:01</MAJ>
    <DATE_VALID></DATE_VALID>
    <LON>2.43544</LON>
    <LAT>48.8409324192598</LAT>
    <STATUT>pending2</STATUT>
    <SOURCE>SIG-GC</SOURCE>
    <VERSION>1_0_0</VERSION>
    <ID_DEP>94</ID_DEP>
    <DEPARTEMENT>Val-de-Marne</DEPARTEMENT>
    <COMMUNE>Vincennes</COMMUNE>
    <COMMENTAIRE>La nouvelle maison d'Alexia !!</COMMENTAIRE>
    <ID_AUTEUR>349</ID_AUTEUR>
    <AUTEUR>npourre</AUTEUR>
    <ID_GEOGROUPE>8</ID_GEOGROUPE>
    <GROUPE>Groupe Test</GROUPE>
    <ID_PARTITION>0</ID_PARTITION>
    
    <DOC>http://demo-ripart.ign.fr/IMG/geoportail/chateau.jpg</DOC>
    
<CROQUIS xmlns:gml="http://www.opengis.net/gml">
 <objet type="Ligne">
  <nom></nom>
  <geometrie>
   <gml:LineString>
    <gml:coordinates>2.4339762392817006,48.842207943841856 2.4338300312714241,48.841065067421965 2.4375536857635289,48.84075901397793</gml:coordinates>
   </gml:LineString>
  </geometrie>
  <attributs>
   <attribut name="calque">troncon_de_route</attribut>
  </attributs>
 </objet>
 <objet type="Polygone">
  <nom></nom>
  <geometrie>
   <gml:Polygon>
    <gml:outerBoundaryIs>
     <gml:LinearRing>
      <gml:coordinates>2.4351357421438293,48.844326462512221 2.4373874410462149,48.844137191275877 2.4370076346344733,48.841917666253359 2.4367477756209692,48.841944997614775 2.4366690770812189,48.841221243653521 2.4346626300836904,48.841411660563104 2.4348830195357563,48.842364522038572 2.4342044722581173,48.84243746027709 2.434284481445351,48.843037484930342 2.4349627268642022,48.842993099391343 2.4351357421438293,48.844326462512221</gml:coordinates>
     </gml:LinearRing>
    </gml:outerBoundaryIs>
   </gml:Polygon>
  </geometrie>
  <attributs>
   <attribut name="calque">batiment</attribut>
  </attributs>
 </objet>
</CROQUIS>
    
    <GEOREP>
        <ID_GEOREP>1284</ID_GEOREP>
        <ID_AUTEUR>349</ID_AUTEUR>
        <AUTEUR>npourre</AUTEUR>
        <TITRE>Reponse automatique</TITRE>
        <STATUT>pending2</STATUT>
        <DATE>2014-12-03 16:42:01</DATE>
        <REPONSE>
Démonstration devant Alexandre.
        </REPONSE>
    </GEOREP>
    <GEOREP>
        <ID_GEOREP>1282</ID_GEOREP>
        <ID_AUTEUR>349</ID_AUTEUR>
        <AUTEUR>npourre</AUTEUR>
        <TITRE>Reponse automatique</TITRE>
        <STATUT>pending1</STATUT>
        <DATE>2014-12-02 14:30:12</DATE>
        <REPONSE>
Démo devant Loïc.
        </REPONSE>
    </GEOREP>
    <GEOREP>
        <ID_GEOREP>1281</ID_GEOREP>
        <ID_AUTEUR>349</ID_AUTEUR>
        <AUTEUR>npourre</AUTEUR>
        <TITRE>Reponse automatique</TITRE>
        <STATUT>reject0</STATUT>
        <DATE>2014-12-01 17:24:27</DATE>
        <REPONSE>
Elle rève !!
        </REPONSE>
    </GEOREP>
    
</GEOREM>
</geors>"""

    xmlaut2=u"""<?xml version='1.0' encoding='UTF-8'?>
<geors version='0.1'>
    <REPONSE type='geoaut_get'>
        <ERREUR code='OK'>OK</ERREUR>
        <JETON>152628375956091cbf658ff2.15839337</JETON>
        <SITE>Demo-RIPart</SITE>
    </REPONSE>
    <AUTEUR>
        <NOM>mborne</NOM>
        <STATUT>1comite</STATUT>
        <STATUTXT>R dacteur</STATUTXT>
    </AUTEUR>
    <PROFIL>
        <ID_GEOPROFIL>277</ID_GEOPROFIL>
        <TITRE>profil éèà</TITRE>
        <ZONE>FXX</ZONE>
        <ID_GEOGROUPE>8</ID_GEOGROUPE>
        <GROUPE>Groupe Test</GROUPE>
        <LOGO>http://demo-ripart.ign.fr/IMG/rubon8.jpg</LOGO>
        <FILTRE/>
        <PRIVE>0</PRIVE>
    </PROFIL>
    <THEMES>   
        <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Route</NOM>
        </THEME>

        <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Adresse, Lieux-dits</NOM>
        </THEME>

        <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Points d'intérêt</NOM>
        </THEME>

        <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Bâti</NOM>
        </THEME>

        <THEME>
            <ID_GEOGROUPE>7</ID_GEOGROUPE> 
            <NOM>Administratif</NOM>
        </THEME>
        <THEME>
            <ID_GEOGROUPE>21</ID_GEOGROUPE> 
            <NOM>Sentier, GR</NOM>
        </THEME>

        <THEME>
            <ID_GEOGROUPE>21</ID_GEOGROUPE> 
            <NOM>Parcelles, Cadastre</NOM>
        </THEME>

        <THEME>
            <ID_GEOGROUPE>21</ID_GEOGROUPE> 
            <NOM>Autre</NOM>
        </THEME>
        <THEME>
            <ID_GEOGROUPE>11</ID_GEOGROUPE> 
            <NOM>@BDCarthage</NOM>
        </THEME>
        <THEME>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Voeux</NOM>
        </THEME>

        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Voeux</NOM>
            <ATT>Type</ATT>
            <TYPE>list</TYPE>
            <VALEURS>&lt;VAL&gt;&lt;/VAL&gt;&lt;VAL&gt;Santé&lt;/VAL&gt;&lt;VAL&gt;Joie&lt;/VAL&gt;&lt;VAL&gt;Amour&lt;/VAL&gt;&lt;VAL&gt;Bonheur&lt;/VAL&gt;&lt;VAL&gt;Sérénité&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>   
        <THEME>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
        </THEME>

        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
            <ATT>Type de voie</ATT>
            <TYPE>text</TYPE>
            <VALEURS>&lt;VAL&gt;&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>  
        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
            <ATT>Type 2</ATT>
            <TYPE>list</TYPE>
            <VALEURS>&lt;VAL&gt;&lt;/VAL&gt;&lt;VAL&gt;autoroute&lt;/VAL&gt;&lt;VAL&gt;route principale&lt;/VAL&gt;&lt;VAL&gt;route secondaire&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>   
        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
            <ATT>type 3</ATT>
            <TYPE>checkbox</TYPE>
            <VALEURS>&lt;VAL&gt;nature&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>

        <ATTRIBUT>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Gestion des routes</NOM>
            <ATT>toto</ATT>
            <TYPE>list</TYPE>
            <VALEURS>&lt;VAL&gt;toto&lt;/VAL&gt;&lt;VAL&gt;titi&lt;/VAL&gt;&lt;VAL&gt;tutu&lt;/VAL&gt;</VALEURS>
        </ATTRIBUT>

        <THEME>
            <ID_GEOGROUPE>8</ID_GEOGROUPE> 
            <NOM>Défense</NOM>
        </THEME>
    </THEMES>
    <GEOGROUPE>
        <ID_GEOGROUPE>8</ID_GEOGROUPE>
        <NOM>Groupe Test</NOM>
        <ADMIN/>
    </GEOGROUPE>
    <GEOGROUPE>
        <ID_GEOGROUPE>50</ID_GEOGROUPE>
        <NOM>ICPE</NOM>
        <ADMIN/>
    </GEOGROUPE>
</geors>"""


    xmlValid= u"""<?xml version='1.0' encoding='UTF-8'?>
<geors version='0.1'>
<REPONSE type='connect'>
    <ERREUR code='OK'>OK</ERREUR>
    <ALEA1>484376529560287b9419a75.70279673</ALEA1>
    <ALEA2>286485418560291c537f0a9.13606656</ALEA2>
    <SITE>Demo-RIParté</SITE>
</REPONSE>
</geors>"""
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_responseValidity(self):
        xmlresponse= XMLResponse(self.xml1)
        
        result=xmlresponse.checkResponseValidity()
        
        self.assertEquals(result['code'], 'OK')
        self.assertEquals(result['message'], 'OK')
        
    def test_responseValidity2(self):
        xmlresponse= XMLResponse(self.xmlValid)
        
        result=xmlresponse.checkResponseValidity()
        
        self.assertEquals(result['code'], 'OK')
        self.assertEquals(result['message'], 'OK')
        
        
    def test_getAleas(self):
        xmlr= XMLResponse(self.xmlAleas)
        result=xmlr.getAleas()
        
        self.assertEquals(len(result),2,"not 2 aleas")
        self.assertEquals(result[0],"50477801556023f1894d172.93762979" ,"first alea incorrect")
        self.assertEquals(result[1],"484376529560287b9419a75.70279673" ,"second alea incorrect")
        self.assertNotEquals(result[1],"484376529560287b9419a75" ,"second alea incorrect")
        
    def test_connectValues(self):
        xmlr= XMLResponse(self.xmlConnectValues)
        result = xmlr.getConnectValues()
        #  connectValues = {'ID_AUTEUR':None,'JETON':None, 'SITE':None}
        
        self.assertEquals(result['ID_AUTEUR'],'354')
        self.assertEquals(result['JETON'],'102814614056091cbf5b4104.13262433')
        self.assertEquals(result['SITE'],'Demo-RIPart')
        
        
    def test_getCurrentJeton(self):
        xmlr= XMLResponse(self.xmlConnectValues)  
        result=xmlr.getCurrentJeton()  
        self.assertEquals(result,'102814614056091cbf5b4104.13262433')
        
    
    def test_getCurrentJetonFailure(self):
        xmlr= XMLResponse(self.xml1)
        with self.assertRaises(Exception) as context:
            xmlr.getCurrentJeton()            
        self.assertTrue('Pas de jeton' in context.exception, "Not the right error message")
      
        
    def test_extractProfil(self):
        xmlr=XMLResponse(self.xmlAut)
        profil = xmlr.extractProfil()
        
        self.assertEquals(profil.id_Geoprofil,'277')
        expected =u'profil éèà'
        self.assertEquals(profil.titre,expected)
       
      
    def test_getThemes(self):
        xmlr=XMLResponse(self.xmlAut)
        themes = xmlr.getThemes()   
        self.assertEquals(len(themes),12)
        
        self.assertEquals(themes[0].groupe.nom,'Route')
        self.assertEquals(themes[0].groupe.id,'7')
        
        
    def test_extractRemarque(self):    
        xmlr =XMLResponse(self.xmlRem)
        remarques=xmlr.extractRemarques()
        
        self.assertEquals(len(remarques),1)
      
        rem=remarques.values()[0]
        
        self.assertEquals(rem.auteur.id,'349')
        self.assertEquals(len(rem.reponses), 3)
        self.assertEquals(rem.reponses[0].id(), '1284')
        self.assertEquals(rem.reponses[0].statut.__str__(), 'pending2')
        
        self.assertEquals(xmlr.getTotalResponse(),'1')
        
    
        
    def test_getClientProfil(self):
        xml = XMLResponse(self.xmlaut2)
        errMessage = xml.checkResponseValidity()
        
    
        self.assertEqual(errMessage['code'], 'OK')
        
        
      
           
            
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()