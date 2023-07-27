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

    def getDataFromGeoservice(self, layer):
        if self.__response is None:
            return layer
        data = self.__response.json()
        # il faut copier le nom de la couche pour récupérer les données de la layer dans la boite "Cherger le guichet"
        layer.name = data['title']
        layer.geoservice.update(data)

    def getDataFromTable(self, layer):
        if self.__response is None:
            return layer
        data = self.__response.json()
        layer.name = data['name']
        layer.description = data['description']
        layer.minzoom = data['min_zoom_level']
        layer.maxzoom = data['max_zoom_level']
        if data['database_versioning'] is True:
            layer.isStandard = False
        layer.tileZoomLevel = data['tile_zoom_level']
        layer.readOnly = data['read_only']
        layer.geometryName = data['geometry_name']
        layer.databasename = data['database']
        layer.wfs = data['wfs']
        layer.wfsTransaction = data['wfs_transactions']
        layer.attributes = data['columns']
        layer.idName = data['id_name']
        for column in data['columns']:
            if column['name'] != layer.geometryName:
                continue
            layer.is3d = column['is3d']
            layer.geometryType = column['type']
            layer.srid = column['srid']
        layer.style = data['style']
        # layer.styles = data['styles']

    def getCommunities(self) -> []:
        communities = []
        if self.__response is None:
            return communities
        data = self.__response.json()
        for cm in data['communities_member']:
            communitie = Group(cm['community_id'], cm['community_name'], cm['emprises'])
            if cm['active']:
                communitie.setActive(True)
            communities.append(communitie)
            # TODO getProfile(cm['profile'] + getThemes)
        return communities

    def extractProfileFromCommunities(self):
        profil = Profil()
        # profil.author.name = ''
        # profil.id_Geoprofil = ''  # TODO trouver l'info
        # ap = self.activeProfile()
        data = self.__response.json()
        profil.title = data['name']
        # TODO revoir initialisation du geogroup
        profil.geogroup.setName(data['name'])
        profil.geogroup.setId(data['id'])
        if 'logo_url' not in data:
            # TODO pourquoi la clé n'existe pas ? quel logo à la place ?
            profil.logo = ""
        else:
            profil.logo = data['logo_url']
        # profil.filtre = ''  # TODO trouver l'info
        # profil.prive = ''  # TODO trouver l'info
        # th = self.getThemesFromCommunities(self.__data['attributes'])
        # profil.themes = th[0]
        # profil.filteredThemes = th[1]
        # profil.globalThemes = None
        # profil.infosGeogroups = self.getInfosGeogroup(self.data['communities_member'], profil)
        return profil
