from ..PluginHelper import PluginHelper


class ThemeAttributes(object):
    """Classe représentant un attribut d'un thème."""

    def __init__(self) -> None:
        self.__name = ''
        self.__title = ''
        self.__type = None
        self.__values = None
        self.__default = None
        self.__required = False
        self.__mandatory = False
        self.__switchNameToTitle = {}

    def setAttributes(self, data) -> None:
        """
        Rempli les attributs d'un thème

        :param data: les données pour les attributs d'un thème
        :type data: dict
        """
        if PluginHelper.keyExist('name', data):
            self.__name = data['name']
        if PluginHelper.keyExist('title', data):
            self.__title = data['title']
        if PluginHelper.keyExist('type', data):
            self.__type = data['type']
        if PluginHelper.keyExist('values', data):
            self.__values = data['values']
        if PluginHelper.keyExist('default', data):
            self.__default = data['default']
        if PluginHelper.keyExist('required', data):
            self.__required = data['required']
        if PluginHelper.keyExist('mandatory', data):
            self.__mandatory = data['mandatory']

    def getName(self) -> str:
        """
        :return: le nom du thème
        """
        return self.__name

    def getTitle(self) -> str:
        """
        :return: le titre du thème
        """
        return self.__title

    def getType(self) -> None:
        """
        :return: le type du thème
        """
        return self.__type

    def getValues(self) -> []:
        """"""
        return self.__values

    def getDefault(self) -> str:
        """"""
        return self.__default

    def getMandatory(self) -> bool:
        """"""
        return self.__mandatory

    def getNameAndTitle(self) -> {}:
        """"""
        return {self.__name: self.__title}

    def switchNameToTitle(self) -> str:
        """"""
        if self.__title != '':
            return self.__title
        return self.__name
