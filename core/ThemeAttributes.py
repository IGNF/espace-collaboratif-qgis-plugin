# Classe représentant un attribut d'un thème
class ThemeAttributes(object):

    def __init__(self) -> None:
        self.__name = ''
        self.__title = ''
        self.__type = None
        self.__values = []
        self.__default = ''
        # self.__inputConstraint = None
        # self.__jsonSchema = None
        # self.__help = None
        self.__required = False
        self.__mandatory = False
        # self.__original = {}

    def keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False

    def getAttributes(self, data) -> None:
        if self.keyExist('name', data):
            self.__name = data['name']
        if self.keyExist('title', data):
            self.__title = data['title']
        if self.keyExist('type', data):
            self.__type = data['type']
        if self.keyExist('values', data):
            self.__values = data['values']
        if self.keyExist('default', data):
            self.__default = data['default']
        if self.keyExist('required', data):
            self.__required = data['required']
        if self.keyExist('mandatory', data):
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

    def getRequired(self) -> bool:
        return self.__required

    def getMandatory(self) -> bool:
        return self.__mandatory

    def setTagDisplay(self, display):
        self.__tagDisplay = display

    def setDefaultValue(self, defaultValue):
        self.__defaultValue = defaultValue

    def setValues(self, values):
        x = values.split('|')
        for value in x:
            self.__values.append(value)
