import os.path
import shutil

from qgis.core import QgsProject
from .PluginLogger import PluginLogger
from .SQLiteManager import SQLiteManager
from ..PluginHelper import PluginHelper


class FlagProject:
    """
    Classe de création d'une propriété personnalisée qui indiquera si le projet ouvert dans QGIS
    est un projet "ESPACE CO" dans le cas ou l'utilisateur a cliqué sur au moins l'un des boutons du menu "ESPACE CO".
    Si ce flag n'existe pas dans le projet alors la copie automatique de fichiers de paramétrage est annulée.
    """
    def __init__(self):
        """
        Constructeur.
        """
        # Instance du projet
        self.__projectInstance = QgsProject.instance()
        # Nom du projet
        self.__projectName = self.__projectInstance.fileName().split("/")[-1].replace(".qgz", "")
        # Répertoire du projet utilisateur
        self.__projectDirectory = QgsProject.instance().homePath()
        # Fichier de log
        self.__logger = PluginLogger("FlagProject").getPluginLogger()
        # répertoire du plugin
        self.__plugin_path = (os.path.dirname(os.path.realpath(__file__))).replace("core", "")
        # Version de QGIS
        self.__versionQGis = self.getVersionQGIS()
        # Répertoire de stockage des fichiers utiles à l'utilisation du plugin
        self.__storageDirectory = self.__plugin_path + PluginHelper.ripart_files_dir + os.path.sep
        self.__styleFilesDir = self.__projectDirectory + os.path.sep + PluginHelper.qmlStylesDirectory
        self.__dbPath = SQLiteManager.getBaseSqlitePath()
        self.__espacecoxml = self.__projectDirectory + os.path.sep + PluginHelper.getConfigFile()

    def __getKeyEntry(self) -> str:
        """
        Construction d'une chaine de caractères correspondant à une clé personnalisée.

        :return: la propriété personnalisée sous forme de "flag"
        """
        return "{}_key".format(self.__projectName)

    def __setScope(self, scope) -> str:
        """
        Construction d'une chaine de caractères correspondant à une clé personnalisée.

        :return: la propriété personnalisée sous forme de "flag"
        """
        return "project_{}".format(scope)

    def setWriteBoolEntryInProject(self):
        """
        Cette méthode permet d’écrire une valeur booléenne dans le fichier de projet QGIS qui indiquera si c'est
        un projet qui a été ouvert pour travailler sur l'espace collaboratif. L'utilisateur à utiliser le menu dédié.
        """
        keyEntry = self.__getKeyEntry()
        scope = self.__setScope(keyEntry)
        self.__projectInstance.writeEntryBool(scope, keyEntry, True)

    def isBoolEntryInProject(self):
        """
        :return: True si la clé personnalisée est retrouvée dans le projet Espace Collaboratif, False sinon
        """
        keyEntry = self.__getKeyEntry()
        scope = self.__setScope(keyEntry)
        # Est-ce qu'elle existe ?
        res = self.__projectInstance.readBoolEntry(scope, keyEntry)
        # si oui, c'est un projet "ESPACE CO"
        if not res[1]:
            return False
        return True

    def copyFilesToProject(self) -> None:
        """
        Copie les fichiers nécessaires au bon fonctionnement du plugin espace collaboratif.
        Ces fichiers se trouvent ici dans le répertoire du plugin : .../espace-collaboratif-qgis-plugin/files

        NB : une exception est envoyée à l'utilisateur si la copie s'est mal passée.
        """
        try:
            # Contrôle l'existence du fichier de configuration
            self.checkConfigFile()
            # Copie de la base de données SQLite
            self.copySQLiteDatabase()
            # Copie des fichiers de style graphique pour les couches signalement et croquis
            # .../espace-collaboratif-qgis-plugin/files/espacecoStyles
            self.copyStyleFiles()
        except Exception as e:
            self.__logger.error("init contexte:" + format(e))
            raise

    def AreFilesCopiedInProject(self) -> bool:
        """
        Est-ce que les fichiers utiles à l'utilisation du plugin QGIS sont présents dans le projet ?

        :return: False si au moins un fichier n'existe pas, True sinon
        """
        if not os.path.isfile(self.__dbPath):
            return False

        if os.path.isdir(self.__styleFilesDir):
            if len(os.listdir(self.__styleFilesDir)) != 4:
                return False

        if not os.path.isfile(self.__espacecoxml):
            return False

        return True

    def checkConfigFile(self):
        """
        Contrôle l'existence du fichier de configuration (nomProjet_espaceco.xml) dans le répertoire du projet (fichier
        nomProjet.qgz). Le fichier est copié s'il n'est pas trouvé dans le répertoire du projet utilisateur.

        NB : une exception est envoyée si le fichier n'est pas trouvé dans le répertoire du projet plugin.
        """
        global nameFile
        if not os.path.isfile(self.__espacecoxml):
            try:
                nameFile = self.__storageDirectory + PluginHelper.nom_Fichier_Parametres_EspaceCo
                shutil.copy(nameFile, self.__espacecoxml)
                self.__logger.debug("Copy {}".format(nameFile))
            except Exception as e:
                self.__logger.error("No {} found in plugin directory\n{}".format(nameFile, e))
                raise Exception("Le fichier de configuration {} n'a pas été trouvé.".format(nameFile))

    def copyStyleFiles(self):
        """
        Copie les fichiers de styles (pour la représentation graphique des signalements et croquis) à l'emplacement
        suivant :
        - projet/espacecoStyles/Croquis_EC_Point.qml
        - projet/espacecoStyles/Croquis_EC_Ligne.qml
        - projet/espacecoStyles/Croquis_EC_Polygone.qml
        - projet/espacecoStyles/Signalement.qml
        """
        global nameFiles
        if not os.path.isfile(self.__styleFilesDir):
            try:
                nameFiles = self.__storageDirectory + PluginHelper.qmlStylesDirectory
                shutil.copytree(nameFiles, self.__styleFilesDir)
                self.__logger.debug("Copy {}".format(nameFiles))
            except Exception as e:
                self.__logger.error("No files found in plugin directory {}.\n{}".format(nameFiles, e))
                raise Exception("Les fichiers de style n'ont pas été trouvés "
                                "dans le répertoire du plugin {}.".format(nameFiles))

    def copySQLiteDatabase(self) -> None:
        """
        Copie du fichier de la base de données SQLite si elle n'existe pas dans le répertoire du projet.

        NB : envoi une Exception si la copie est impossible.
        """
        global nameFile
        if not os.path.isfile(self.__dbPath):
            try:
                nameFile = self.__storageDirectory + PluginHelper.ripart_db
                shutil.copy(nameFile, self.__dbPath)
                self.__logger.debug("Copy {}".format(nameFile))
            except Exception as e:
                self.__logger.error("No {} found in plugin directory.\n{}".format(nameFile, e))
                raise Exception("Le fichier de configuration {} n'a pas été trouvé.".format(nameFile))

    def getVersionQGIS(self) -> int:
        """
        :return: la version de QGIS
        """
        try:
            # QGIS 3.x
            from qgis.core import Qgis
            version = Qgis.version() if hasattr(Qgis, 'version') else Qgis.versionInt()
            message = "QGIS {} détecté".format(version)
        except ImportError:
            # QGIS 2.x
            from qgis.core import Qgis as Qgis
            version = Qgis.versionInt()
            message = "QGIS {} détecté".format(version)
        print(message)
        self.__logger.debug(message)
        return version
