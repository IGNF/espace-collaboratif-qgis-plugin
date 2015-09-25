# -*- coding: utf-8 -*-
'''
Created on 26 janv. 2015

@author: AChang-Wailing
'''
import logging
import lib.requests as requests

class RipartServiceRequest(object):
    """
    Classe pour les requêtes http vers le service ripart
    """

    logger= logging.getLogger("ripart.RipartServiceRequest")

    @staticmethod
    def  makeHttpRequest(url, params=None, data=None, files=None):  
        """  Effectue une requête HTTP GET ou POST
        
        :param url: url de base de la requête
        :type url: string
        :param params: paramètres à passer (sous forme de dictionnaire) pour une requête GET
        :type params: Dictionary
        :param data : paramètres pour une requête POST
        :type data: Dictionary
        :param files : fichiers à uploader
        :type files: Dictionary

        :return la réponse du serveur (xml)
        :rtype: string
        """
        response= ""        
        try: 
            if (data ==None and files ==None):   
                r = requests.get(url,params=params, verify=False)
            else :
                r= requests.post(url, data=data,files=files, verify=False)
     
            r.encoding ='utf-8'
            response=r.text
        except Exception as e:
            RipartServiceRequest.logger.error(str(e))
            raise
        
        return  response
    
    
    
    
    

    """def  makeHttpRequest0(url, params):
    
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
        
      """  
  
        
        
        
