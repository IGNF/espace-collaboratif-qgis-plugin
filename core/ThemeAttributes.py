# Classe représentant un attribut d'un thème
class ThemeAttributes(object):

    def __init__(self) -> None:
        self.__name = ''
        self.__title = ''
        self.__type = None
        self.__values = None
        self.__default = None
        # self.__inputConstraint = None
        # self.__jsonSchema = None
        # self.__help = None
        # TODO voir avec Noémie la différence entre obligatoire et requis
        self.__required = False
        self.__mandatory = False
        # self.__original = {}
        self.__switchNameToTitle = {}

    def __keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False

    def setAttributes(self, data) -> None:
        if self.__keyExist('name', data):
            self.__name = data['name']
        if self.__keyExist('title', data):
            self.__title = data['title']
        if self.__keyExist('type', data):
            self.__type = data['type']
        if self.__keyExist('values', data):
            self.__values = data['values']
        if self.__keyExist('default', data):
            self.__default = data['default']
        if self.__keyExist('required', data):
            self.__required = data['required']
        if self.__keyExist('mandatory', data):
            self.__mandatory = data['mandatory']

    def getName(self) -> str:
        return self.__name

    def getTitle(self) -> str:
        return self.__title

    def getType(self) -> None:
        return self.__type

    def getValues(self) -> []:
        return self.__values

    def getDefault(self) -> str:
        return self.__default

    def getMandatory(self) -> bool:
        return self.__mandatory

    def getNameAndTitle(self) -> {}:
        return {self.__name: self.__title}

    def switchNameToTitle(self) -> str:
        if self.__title != '':
            return self.__title
        return self.__name
