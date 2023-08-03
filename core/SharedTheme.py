from .Theme import Theme


# Classe représentant un thème
class SharedTheme(object):

    def __init__(self) -> None:
        self.__communityId = -1
        self.__communityName = ''
        self.__themes = []

    def keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False

    def getSharedTheme(self, data) -> None:
        if self.keyExist('community_id', data):
            self.__communityId = data['community_id']
        if self.keyExist('community_name', data):
            self.__communityName = data['community_name']
        if self.keyExist('themes', data):
            self.getDatasSharedTheme(data['themes'])

    def getDatasSharedTheme(self, datas) -> None:
        if len(datas) == 0:
            return
        for data in datas:
            theme = Theme()
            theme.getTheme(data)
            self.__themes.append(theme)

    def getCommunityId(self) -> int:
        return self.__communityId

    def getCommunityName(self) -> str:
        return self.__communityName

    def getThemes(self) -> []:
        return self.__themes
