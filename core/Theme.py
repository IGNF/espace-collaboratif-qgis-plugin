from .ThemeAttributes import ThemeAttributes


# Classe représentant un thème
class Theme(object):

    def __init__(self, communityId) -> None:
        self.__communityId = communityId
        self.__name = ''
        self.__global = False
        # TODO -> Noémie ce help est-il utile ?
        # self.__help = ''
        self.__database = ''
        self.__featureType = ''
        self.__attributes = []
        self.__switchNameToTitle = {}

    def setTheme(self, data) -> None:
        if type(data) is str:
            self.__name = data
        else:
            if self.__keyExist('theme', data):
                self.__name = data['theme']
            if self.__keyExist('global', data):
                self.__global = data['global']
            if self.__keyExist('database', data):
                self.__database = data['database']
            if self.__keyExist('featureType', data):
                self.__featureType = data['featureType']
            if self.__keyExist('attributes', data):
                self.__setDataAttributes(data['attributes'])

    def getCommunityId(self) -> int:
        return self.__communityId

    def getName(self) -> str:
        return self.__name

    def getAttributes(self) -> []:
        return self.__attributes

    def getSwitchAttributeNameToTitle(self, name) -> str:
        title = ''
        if name in self.__switchNameToTitle:
            title = self.__switchNameToTitle[name]
        return title

    def __setDataAttributes(self, datas) -> None:
        if len(datas) == 0:
            return
        for data in datas:
            themeAttributes = ThemeAttributes()
            themeAttributes.setAttributes(data)
            self.__attributes.append(themeAttributes)
            self.__switchNameToTitle.update(themeAttributes.getNameAndTitle())

    def __keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False
