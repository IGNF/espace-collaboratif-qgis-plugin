from .NoProfileException import NoProfileException
from .Profil import Profil
from .InfosGeogroup import InfosGeogroup
from .Layer import Layer
from .ThemeAttributes import ThemeAttributes


class JsonResponse(object):
    # Python requests.Response Object
    __response = None
    # Python requests.Response.text (les données recherchées par la requête)
    __data = None

    def __init__(self, response):
        self.__response = response

    def readData(self):
        self.__data = self.__response.json()

    def checkResponseValidity(self):
        if not self.__response.ok:
            err = "code : {0}, message : {1}".format(self.__response.status_code, self.__response.reason)
            raise NoProfileException(err)

    def activeProfile(self):
        if self.__data is None:
            return "", "", ""
        for cm in self.__data['communities_member']:
            if not cm['active']:
                continue
            return cm['community_name'], cm['community_id'], cm['profile']

    def getUserName(self):
        return self.__data['username']

    def getAttributes(self):
        themesAttDict = {}
        thAttributes = []
        for attribute in self.__data['attributes']:
            for attributes in attribute:
                th = ThemeAttributes(attribute['theme'], attributes['name'], '')
                if 'type' in attributes:
                    th.setType(attributes['type'])
                if 'mandatory' in attributes:
                    th.setMandatory()
                if 'default' in attributes:
                    th.setDefaultValue(attributes['default'])
                if 'values' in attributes:
                    th.setValues(attributes['values'])
                if 'autofill' in attributes:
                    a = 2
                thAttributes.append(th)
        return themesAttDict








        for attNode in thAttNodes:

            nomTh = ClientHelper.notNoneValue(attNode.find('NOM').text)
            attNodeATT = attNode.find('ATT')
            nomAtt = attNodeATT.text
            thAttribut = ThemeAttribut(nomTh, nomAtt, "")
            thAttribut.setTagDisplay(nomAtt)
            display_tag = attNodeATT.get('display')
            if display_tag is not None:
                thAttribut.setTagDisplay(display_tag)

            attType = attNode.find('TYPE').text
            thAttribut.setType(attType)

            attObligatoire = attNode.find('OBLIGATOIRE')
            if attObligatoire is not None:
                thAttribut.setObligatoire()

            for val in attNode.findall('VALEURS/VAL'):
                valDisplay = val.get('display')
                if valDisplay is not None:
                    thAttribut.addValeur(val.text, valDisplay)
                else:
                    thAttribut.addValeur(val.text, "")

            for val in attNode.findall('VALEURS/DEFAULTVAL'):
                thAttribut.defaultval = val.text

            thAttributs.append(thAttribut)
            if nomTh not in themesAttDict:
                themesAttDict[nomTh] = []
            themesAttDict[nomTh].append(thAttribut)

        return themesAttDict



    def extractProfile(self):
        profil.globalThemes = None
        profil.infosGeogroups = self.getInfosGeogroup(self.data['communities_member'], profil)
        return profil

    def getInfosGeogroup(self, communities_member, profil):
        """Extraction des infos utilisateur sur ses geogroupes
        :return les infos
        """
        global infosgeogroup
        infosgeogroups = []
        for cm in communities_member:
            infosgeogroup = InfosGeogroup()
            infosgeogroup.group.name = cm['community_name']
            infosgeogroup.group.id = cm['community_id']
            #infosgeogroup.georemComment = ''  # TODO trouver l'info
            th = self.getThemesFromUsers(cm['profile'])
            infosgeogroup.themes = th[0]
            profil.allThemes.append(th[0])
            infosgeogroup.filteredThemes = th[1]
            layer = Layer()
            infosgeogroup.layers.append(layer)
            infosgeogroups.append(infosgeogroup)
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

    def extractProfileFromCommunities(self):
        profil = Profil()
        #profil.author.name = ''
        # profil.id_Geoprofil = ''  # TODO trouver l'info
        #ap = self.activeProfile()
        profil.title = self.data['name']
        profil.geogroup.name = self.data['name']
        profil.geogroup.id = self.data['id']
        profil.logo = self.data['logo_url']
        # profil.filtre = ''  # TODO trouver l'info
        # profil.prive = ''  # TODO trouver l'info
        th = self.getThemesFromCommunities(self.data['attributes'])
        profil.themes = th[0]
        profil.filteredThemes = th[1]
        profil.globalThemes = None
        #profil.infosGeogroups = self.getInfosGeogroup(self.data['communities_member'], profil)
        return profil

    def getThemesFromCommunities(self, communitiesAttributes):
        themes = []
        return themes