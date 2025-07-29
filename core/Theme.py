from .ThemeAttributes import ThemeAttributes
from ..PluginHelper import PluginHelper


class Theme(object):
    """
    Classe représentant un thème.
    """

    def __init__(self, communityId) -> None:
        """
        Constructeur.

        :param communityId: l'identifiant de groupe
        :type communityId: int
        """
        self.__communityId = communityId
        self.__name = ''
        self.__global = False
        self.__database = ''
        self.__featureType = ''
        self.__attributes = []
        self.__switchNameToAlias = {}

    def setTheme(self, data) -> None:
        """
        Remplit les attributs généraux d'un thème.

        :param data: les données générales d'un thème
        :type data: dict
        """
        if type(data) is str:
            self.__name = data
        else:
            if PluginHelper.keyExist('theme', data):
                self.__name = data['theme']
            if PluginHelper.keyExist('global', data):
                self.__global = data['global']
            if PluginHelper.keyExist('database', data):
                self.__database = data['database']
            if PluginHelper.keyExist('featureType', data):
                self.__featureType = data['featureType']
            if PluginHelper.keyExist('attributes', data):
                self.__setDataAttributes(data['attributes'])

    def getCommunityId(self) -> int:
        """
        :return: l'identifiant du groupe auquel appartient l'utilisateur
        """
        return self.__communityId

    def getName(self) -> str:
        """
        :return: le nom du thème
        """
        return self.__name

    def getAttributes(self) -> []:
        """
        :return: les attributs constituant le thème
        """
        return self.__attributes

    def getSwitchAttributeNameToAlias(self, name) -> str:
        """
        Retrouve l'alias du thème en fonction de son nom.

        :param name: le nom du thème
        :type name: str

        :return: l'alias du thème
        """
        alias = ''
        if name in self.__switchNameToAlias:
            alias = self.__switchNameToAlias[name]
        return alias

    def __setDataAttributes(self, datas) -> None:
        """
        Remplit les attributs d'un thème.

        :param datas: liste des attributs
        :type datas: list
        """
        if len(datas) == 0:
            return
        for data in datas:
            themeAttributes = ThemeAttributes()
            themeAttributes.setAttributes(data)
            self.__attributes.append(themeAttributes)
            self.__switchNameToAlias.update(themeAttributes.getNameAndAlias())
