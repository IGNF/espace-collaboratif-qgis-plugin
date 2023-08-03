from .Theme import Theme


# Classe représentant un thème
class ActiveTheme(object):

    def __init__(self) -> None:
        self.__groupId = -1
        self.__groupName = ''
        self.__themes = []

    def keyExist(self, key, data) -> bool:
        if key in data:
            return True
        return False

    def getActiveTheme(self, data) -> None:
        if self.keyExist('group_id', data):
            self.__groupId = data['group_id']
        if self.keyExist('group_name', data):
            self.__groupName = data['group_name']
        if self.keyExist('themes', data):
            self.getDatasActiveTheme(data['themes'])

    def getDatasActiveTheme(self, datas) -> None:
        if len(datas) == 0:
            return
        for data in datas:
            theme = Theme()
            theme.getTheme(data)
            self.__themes.append(theme)

    def getGroupId(self) -> int:
        return self.__groupId

    def getGroupName(self) -> str:
        return self.__groupName

    def getThemes(self) -> []:
        return self.__themes