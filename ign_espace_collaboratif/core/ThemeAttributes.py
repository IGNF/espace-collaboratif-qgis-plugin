from ..PluginHelper import PluginHelper


class ThemeAttributes(object):
    """
    Classe représentant un attribut d'un thème.
    """

    def __init__(self) -> None:
        """
        Initialisation des attributs d'un thème.
        """
        self.__name = ''
        self.__nameAlias = ''
        self.__type = None
        self.__values = None
        self.__default = None
        self.__required = False
        self.__mandatory = False
        self.__multiple = False
        self.__switchNameToAlias = {}

    def setAttributes(self, data) -> None:
        """
        Rempli les attributs d'un thème.

        :param data: les données pour les attributs d'un thème
        :type data: dict
        """
        if PluginHelper.keyExist('name', data):
            self.__name = data['name']
        if PluginHelper.keyExist('title', data):
            self.__nameAlias = data['title']
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
        if PluginHelper.keyExist('multiple', data):
            self.__multiple = bool(data['multiple'])
        elif PluginHelper.keyExist('cardinality', data):
            self.__multiple = str(data['cardinality']).lower() in ('many', 'multiple', 'n')

    def getName(self) -> str:
        """
        :return: le nom du thème
        """
        return self.__name

    def getAlias(self) -> str:
        """
        :return: l'alias du thème (au sens QGIS)
        """
        return self.__nameAlias

    def getType(self) -> str:
        """
        :return: le type de widgets ('checkbox', 'date', 'datetime', 'list') à créer pour initialiser le thème
        """
        return self.__type

    def getValues(self) -> []:
        """
        :return: une liste de valeurs (cas d'un champ liste par exemple)
        """
        return self.__values

    def getDefault(self) -> str:
        """
        :return: la valeur par défaut que peut prendre un attribut
        """
        return self.__default

    def getMandatory(self) -> bool:
        """
        :return: la valeur obligatoire
        """
        return self.__mandatory

    def getMultiple(self) -> bool:
        """
        :return: à True si l'attribut de type 'list' accepte une sélection multiple de valeurs.
                 Dans ce cas, le serveur attend la valeur de l'attribut sous forme de tableau (array).
        """
        return self.__multiple

    def getNameAndAlias(self) -> {}:
        """
        :return: le nom et l'alias de l'attribut
        """
        return {self.__name: self.__nameAlias}

    def switchNameToAlias(self) -> str:
        """
        :return: l'alias si différent de vide
        """
        if self.__nameAlias != '':
            return self.__nameAlias
        return self.__name
