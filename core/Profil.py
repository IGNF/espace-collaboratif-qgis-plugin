from .Author import Author
from .Group import Group
from . import Constantes


class Profil(object):
    """
    Classe représentant le profil de l'utilisateur
    """
    def __init__(self):
        # Nom de l'auteur
        self.author = Author()

        # Nom du Geogroupe
        self.geogroup = Group()

        # Titre du Geogroupe
        self.title = ""

        # Statut (privilèges) du profil
        self.statut = ""

        # Lien vers le logo du profil
        self.logo = ""

        # Filtre du profil
        self.filtre = ""

        # La zone géographique de travail du profil
        self.zone = Constantes.ZoneGeographique.UNDEFINED

        # Indique si le profil a accès aux groupes privés
        self.prive = False

        # Les éventuels thèmes attachés au profil
        # Liste des thèmes du profil actif
        self.themes = list()

        # Liste des noms des thèmes filtrés
        self.filteredThemes = list()

        # Liste de tous les thèmes du profil de l'utilisateur (issus de tous ses groupes)
        self.allThemes = list()

        # Liste des noms des thèmes globaux
        self.globalThemes = list()

        # identifiant geoprofil
        self.id_Geoprofil = ""

        # Les différents groupes de l'utilisateur
        self.infosGeogroups = list()

        # La liste des groupes de l'utilisateur
        self.listGroup = list()
