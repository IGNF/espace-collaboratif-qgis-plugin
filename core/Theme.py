from .ThemeAttributes import ThemeAttributes


# Classe représentant un thème
class Theme(object):

    def __init__(self) -> None:
        self.__name = ''
        self.__global = False
        # self.__help = ''
        self.__database = ''
        self.__featureType = ''
        self.__attributes = []

    def getTheme(self, data) -> None:
        if self.keyExist('theme', data):
            self.__name = data['theme']
        if self.keyExist('global', data):
            self.__global = data['global']
        if self.keyExist('database', data):
            self.__database = data['database']
        if self.keyExist('featureType', data):
            self.__featureType = data['featureType']
        if self.keyExist('attributes', data):
            self.getDataAttributes(data['attributes'])

    def getDataAttributes(self, datas) -> None:
        if len(datas) == 0:
            return
        for data in datas:
            themeAttributes = ThemeAttributes()
            themeAttributes.getAttributes(data)
            self.__attributes.append(themeAttributes)

    def getName(self) -> str:
        return self.__name

    def getGlobal(self) -> bool:
        return self.__global

    def getDatabase(self) -> str:
        return self.__database

    def getFeatureType(self) -> str:
        return self.__featureType

    def getAttributes(self) -> []:
        return self.__attributes

    def keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False
