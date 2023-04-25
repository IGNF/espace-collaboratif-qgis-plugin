from .NoProfileException import NoProfileException
from .Profil import Profil
from .Group import Group


class JsonResponse(object):
    # Python requests.Response Object
    response = ""
    # Python requests.Response.text (les données recherchées par la requête)
    data = ""

    def __init__(self, response):
        self.response = response

    def readData(self):
        self.data = self.response.json()

    def checkResponseValidity(self):
        if not self.response.ok:
            err = "code : {0}, message : {1}".format(self.response.status_code, self.response.reason)
            raise NoProfileException(err)

    def activeProfile(self):
        for cm in self.data['communities_member']:
            if not cm['active']:
                continue
            return cm['community_name'], cm['community_id']

    def extractProfile(self):
        profil = Profil()
        profil.author.name = self.data['username']
        # profil.id_Geoprofil = self.data[''] pas l'info
        profil.title = self.activeProfile()[0]
        profil.geogroup.name = self.activeProfile()[0]
        profil.geogroup.id = self.activeProfile()[1]
        # profil.logo = self.data[''] pas l'info
        # profil.filtre = self.data[''] pas l'info
        # profil.prive = self.data[''] pas l'info
        profil.themes = self.getThemes()
        profil.infosGeogroups = self.getInfosGeogroup(profil)
        return profil

    def getThemes(self):
        themes = []
        # try:
        #     themesAttDict = self.get_themes_attributes(self.root.findall('THEMES/ATTRIBUT'))
        #
        #     # Récupération du filtre sur les thèmes
        #     filterDict = self.root.find('PROFIL/FILTRE').text
        #     filteredThemes = []
        #     globalThemes = []
        #     if filterDict is not None:
        #         groupFilters = re.findall('\{.*?\}', filterDict)
        #         filteredThemes = self.getFilteredThemes(groupFilters, "")
        #
        #     nodes = self.root.findall('THEMES/THEME')
        #
        #     for node in nodes:
        #         theme = Theme()
        #         theme.group = Group()
        #
        #         name = (node.find('NOM')).text
        #         theme.group.name = name
        #         if name in filteredThemes or len(filteredThemes) == 0:
        #             theme.isFiltered = True
        #
        #         isGlobal = (node.find('GLOBAL')).text
        #         if isGlobal == '1':
        #             theme.isGlobal = True
        #             globalThemes.append(name)
        #
        #         theme.group.id = (node.find('ID_GEOGROUPE')).text
        #         if ClientHelper.notNoneValue(theme.group.name) in themesAttDict:
        #             theme.attributes.extend(themesAttDict[ClientHelper.notNoneValue(theme.group.name)])
        #         themes.append(theme)
        #
        # except Exception as e:
        #     self.logger.error(str(e))
        #     raise Exception("Erreur dans la récupération des thèmes du profil : {}".format(str(e)))
        #
        # return [themes, filteredThemes, globalThemes]
        return themes

    def getInfosGeogroup(self, profil):
        """Extraction des infos utilisateur sur ses geogroupes
        :return les infos
        """
        global infosgeogroup
        infosgeogroups = []

        # try:
        #     # informations sur le geogroupe
        #     nodesGr = self.root.findall('GEOGROUPE')
        #     for nodegr in nodesGr:
        #         infosgeogroup = InfosGeogroup()
        #         infosgeogroup.group = Group()
        #         infosgeogroup.group.name = (nodegr.find('NOM')).text
        #         infosgeogroup.group.id = (nodegr.find('ID_GEOGROUPE')).text
        #
        #         # Récupération du commentaire par défaut des signalements
        #         infosgeogroup.georemComment = nodegr.find('COMMENTAIRE_GEOREM').text
        #
        #         # Récupération des layers du groupe
        #         for nodelayer in nodegr.findall('LAYERS/LAYER'):
        #             layer = Layer()
        #             layer.type = nodelayer.find('TYPE').text
        #             layer.nom = nodelayer.find('NOM').text
        #             layer.description = nodelayer.find('DESCRIPTION').text
        #             layer.minzoom = nodelayer.find('MINZOOM').text
        #             layer.maxzoom = nodelayer.find('MAXZOOM').text
        #             layer.extent = nodelayer.find('EXTENT').text
        #             # cas particulier de la balise <ROLE> qui n'existe
        #             # que dans la base de qualification
        #             role = nodelayer.find('ROLE')
        #             if role is not None:
        #                 layer.role = role.text
        #             layer.visibility = nodelayer.find('VISIBILITY').text
        #             layer.opacity = nodelayer.find('OPACITY').text
        #             tilezoom = nodelayer.find('TILEZOOM')
        #             if tilezoom is not None:
        #                 layer.tilezoom = tilezoom.text
        #             url = nodelayer.find('URL')
        #             if url is None or url.text is None:
        #                 continue
        #             layer.url = url.text
        #             layer.databasename = self.findDatabaseName(url.text)
        #             print("groupe : {0} layer : {1} databasename : {2}".format(infosgeogroup.group.name, layer.nom, layer.databasename))
        #             layer_id = nodelayer.find('LAYER')
        #             if layer_id is not None:
        #                 layer.layer_id = layer_id.text
        #             infosgeogroup.layers.append(layer)
        #         try:
        #             # Récupération des thèmes du groupe
        #             themesAttDict = self.get_themes_attributes(nodegr.findall('THEMES/ATTRIBUT'))
        #
        #             nodes = nodegr.findall('THEMES/THEME')
        #
        #             # Récupérer les thèmes à afficher dans le profil (balise <FILTER>)
        #             # Exemple : [{"group_id":375,"themes":["Test_signalement","test leve",
        #             # "Theme_table_bool_TestEcriture"]},{"group_id":1,"themes":["Bati"]}]
        #
        #             filterDict = nodegr.find('FILTER').text
        #             groupFilters = re.findall('\{.*?\}', filterDict)
        #             filteredThemes = self.getFilteredThemes(groupFilters, infosgeogroup.group.id)
        #             infosgeogroup.filteredThemes = filteredThemes
        #
        #             for node in nodes:
        #                 theme = Theme()
        #                 theme.group = Group()
        #
        #                 name = (node.find('NOM')).text
        #                 theme.group.name = name
        #                 if name in filteredThemes:
        #                     theme.isFiltered = True
        #
        #                 theme.group.id = infosgeogroup.group.id
        #                 if ClientHelper.notNoneValue(theme.group.name) in themesAttDict:
        #                     theme.attributes.extend(themesAttDict[ClientHelper.notNoneValue(theme.group.name)])
        #
        #                 infosgeogroup.themes.append(theme)
        #                 profil.allThemes.append(theme)
        #
        #         except Exception as e:
        #             self.logger.error(str(e))
        #             raise Exception("Erreur dans la récupération des thèmes du groupe")
        #
        #         infosgeogroups.append(infosgeogroup)
        #
        # except Exception as e:
        #     self.logger.error(str(e))
        #     raise Exception("Erreur dans la récupération des informations du groupe " + infosgeogroup.group.name)
        return infosgeogroups
