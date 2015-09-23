# -*- coding: utf-8 -*-
'''
Created on 26 janv. 2015

@author: AChang-Wailing
'''
import logging
#import RipartLogger 
import urllib2
import urllib

class RipartServiceRequest(object):
    """
    Classe pour les requêtes http vers le service ripart
    """

    logger= logging.getLogger("ripart.RipartServiceRequest")

    
    @staticmethod
    def  makeGetRequest(url, params):
        """
        Effectue une requête HTTP GET 
        
        :param url: url de base de la requ�te
        :param params: paramètres à passer  (dictionnaire)
        """
        try: 
            data = urllib.urlencode(params)
    
            req = urllib2.Request(url, data)
            
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            '''opener = urllib2.build_opener()
            opener.addheaders = [('Accept-Charset', 'utf-8')]
    
            response = opener.open(req)
               
      
            response_data=response.read()
            '''
            
            response = urllib2.urlopen(req)

            response_data=response.read()
            
        except Exception as e:
            RipartServiceRequest.logger.error(str(e))
            raise
            
        return response_data
        
        
        
        
if __name__ == "__main__":
     
    rep= RipartServiceRequest.makeGetRequest("http://demo-ripart.ign.fr",{'action':'connect','login':'mborne'})
    print rep 
