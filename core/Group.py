# Classe représentant un groupe de l'espace collaboratif


class Group(object):
    def __init__(self, id_group="", name="", emprises=None, active=False):
        # L'identifiant du groupe
        if emprises is None:
            emprises = []
        self.__id = id_group
        # Le nom du groupe
        self.__name = name
        # Indique si le groupe est celui sur lequel l'utilisateur travaille
        self.__active = active
        self.__emprises = emprises

    def getId(self):
        return self.__id

    def getName(self):
        return self.__name

    def getActive(self):
        return self.__active

    def getEmprise(self):
        return self.__emprises

    def setId(self, id):
        self.__id = id

    def setName(self, name):
        self.__name = name

    def setActive(self, active):
        self.__active = active

    def setEmprise(self, emprises):
        self.__emprises = emprises
