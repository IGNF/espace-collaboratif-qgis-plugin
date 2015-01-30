# -*- coding: utf-8 -*-
'''
Created on 26 janv. 2015

@author: AChang-Wailing
'''
import logging
import RipartLogger 
import urllib2
import urllib

class RipartServiceRequest(object):
    '''
    classdocs
    '''

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
    
            response = urllib2.urlopen(req)
               
            d=response.decode('utf-8')
            response_data=response.read()
            
        except Exception as e:
            RipartServiceRequest.logger.error(str(e))
            raise
            
        return response_data
        
        
        
'''if __name__ == "__main__":
     
      rep= RipartServiceRequest.makeGetRequest("http://demo-ripart.ign.fr",{'action':'connect','login':'mborne'})
      print rep 
'''