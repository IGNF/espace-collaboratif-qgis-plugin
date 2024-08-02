from .NoProfileException import NoProfileException
from .Profil import Profil
from .InfosGeogroup import InfosGeogroup
from .Group import Group
from .Layer import Layer
from .ThemeAttributes import ThemeAttributes


class JsonResponse(object):
    # Python requests.Response Object
    __response = None

    def __init__(self, response):
        self.__response = response

    def getNumrec(self):
        numrec = 0
        if self.__response is None:
            return numrec
        data = self.__response.json()
        if not 'numrec' in data:
            return numrec
        return data['numrec']
