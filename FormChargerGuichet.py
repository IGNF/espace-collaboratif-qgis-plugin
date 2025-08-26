import os
from PyQt5.QtWidgets import QDialogButtonBox, QTableWidget
from PyQt5 import QtCore
from qgis.PyQt import uic, QtWidgets
from .PluginHelper import PluginHelper
from .Contexte import Contexte
from .core.BBox import BBox
from .core.NoProfileException import NoProfileException
from .core.SQLiteManager import SQLiteManager
from .core.PluginLogger import PluginLogger
from .core import Constantes as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChargerGuichet_base.ui'))


class FormChargerGuichet(QtWidgets.QDialog, FORM_CLASS):
    """
    Classe du dialogue qui affiche la liste des couches disponibles dans le profil de l'utilisateur.
    Récupération des choix de l'utilisateur pour lancer l'import des couches dans le projet.
    """

    # Balises <ROLE>
    # Role de la couche dans le cadre d'un guichet
    # - visu = couche servant de fond uniquement
    # - ref = couche servant de référence pour la saisie (snapping ou routing)
    # - edit, ref-edit = couche éditable sur le guichet
    # "clé xml":"valeur affichage boite"
    roleCleVal = {"edit": "Edition", "ref-edit": "Edition", "visu": "Visualisation", "ref": "Visualisation"}
    # Booléen qui indique si l'utilisateur a cliqué sur le bouton Annuler ou sur la croix de fermeture de la boite
    bRejected = False

    def __init__(self, context, listLayers, parent=None) -> None:
        """
        Constructeur du dialogue "Charger les couches de mon groupe" et initialisation des différents items
        de la boite.

        NB : appeler dans PluginModule.py, fonction : __downloadLayersFromMyCommunity

        :param context: le contexte du projet
        :type context: Contexte

        :param listLayers: la liste des couches disponibles (Guichet et Fonds Geoservices) dans le profil
                           de l'utilisateur
        :type listLayers: list
        """
        super(FormChargerGuichet, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.__context = context
        self.__logger = PluginLogger("FormChargerGuichet").getPluginLogger()

        # Il faut inverser l'ordre des couches pour retrouver le paramétrage de la carte du groupe sur le site
        self.__listLayers = listLayers
        self.__listLayers.reverse()

        # Remplissage des différentes tables de couches
        self.__setTableWidgetMonGuichet()
        self.__setTableWidgetFondsGeoservices()

        # Réaction au clic sur les boutons "Enregistrer" (Save) et "Annuler" (Cancel)
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.__save)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.__cancel)

        # Réaction au clic sur les boutons "Tout charger", l'ensemble des couches sont cochées automatiquement
        self.pushButton_checkAllBoxes_MonGuichet.clicked.connect(self.__checkAllBoxesMonGuichet)
        self.pushButton_checkAllBoxes_FondsGeoservices.clicked.connect(self.__checkAllBoxesFondsGeoservices)

        # Le nom du groupe (Communauté active) apparait en gras et de couleur bleue
        self.labelGroupeActif.setText("Communauté active : {}".format(context.getUserCommunity().getName()))
        self.labelGroupeActif.setStyleSheet("QLabel {color : blue}")  # #ff0000

    def __checkAllBoxesMonGuichet(self) -> None:
        """
        Si l'utilisateur clique sur un des boutons "Tout charger", l'ensemble des couches de "Mon guichet" sont cochées.
        """
        for i in range(self.tableWidgetMonGuichet.rowCount()):
            item = self.tableWidgetMonGuichet.item(i, 2)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Checked)

    def __checkAllBoxesFondsGeoservices(self) -> None:
        """
        Si l'utilisateur clique sur un des boutons "Tout charger", l'ensemble des couches de "Fonds GéoServices"
        sont cochées.
        """
        for i in range(self.tableWidgetFondsGeoservices.rowCount()):
            item = self.tableWidgetFondsGeoservices.item(i, 2)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Checked)

    def __setColumnCharger(self, tableWidget, row, column, check=False) -> None:
        """
        Initialisation de la dernière colonne "Charger" (position 2) avec des cases à cocher. (Non cochées par défaut)

        :param tableWidget: la vue table générale
        :type tableWidget: QTableWidget

        :param row: le numéro de la ligne de la table
        :type row: int

        :param column: la position de la colonne (Charger) de la table
        :type column: int

        :param check: indique si une case doit être cochée, par défaut à False (non cochée)
        :type check): bool
        """
        itemCheckBox = QtWidgets.QTableWidgetItem()
        itemCheckBox.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        if not check:
            itemCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        else:
            itemCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
        tableWidget.setItem(row, column, itemCheckBox)

    def __setTableWidgetMonGuichet(self) -> None:
        """
        Initialise la vue table "Mon guichet" avec trois colonnes "Nom de la couche", "Rôle" et "Charger"
         - Une ligne par couche avec son nom.
         - Deux rôles pour une couche : "Edition" ou "Visualisation"
         - Une case à cocher par couche (colonne "Charger")
        """
        entete = ["Nom de la couche", "Rôle", "Charger"]
        self.tableWidgetMonGuichet.setHorizontalHeaderLabels(entete)
        self.tableWidgetMonGuichet.setColumnWidth(0, 400)
        self.tableWidgetMonGuichet.setColumnWidth(1, 200)
        self.tableWidgetMonGuichet.setColumnWidth(2, 130)

        # Autres lignes de la table
        for layer in self.__listLayers:
            if layer.type != cst.FEATURE_TYPE:
                continue

            rowPosition = self.tableWidgetMonGuichet.rowCount()
            self.tableWidgetMonGuichet.insertRow(rowPosition)

            # Colonne "Nom de la couche"
            item = QtWidgets.QTableWidgetItem(layer.name())
            self.tableWidgetMonGuichet.setItem(rowPosition, 0, item)

            # Colonne "Rôle"
            role = layer.role
            if role in self.roleCleVal:
                item = QtWidgets.QTableWidgetItem(self.roleCleVal[role])
            else:
                item = QtWidgets.QTableWidgetItem("Pas de rôle, bizarre !")
            self.tableWidgetMonGuichet.setItem(rowPosition, 1, item)
            self.__setColumnCharger(self.tableWidgetMonGuichet, rowPosition, 2)

    def __setTableWidgetFondsGeoservices(self) -> None:
        """
        Initialise la vue table "Fonds Géoservices" avec trois colonnes "Nom de la couche", "Rôle" et "Charger"
         - Une ligne par couche avec son nom.
         - Un seul rôle pour une couche : "Visualisation"
         - Une case à cocher par couche (colonne "Charger")
        """
        # Entête
        entete = ["Nom de la couche", "Rôle", "Charger"]
        self.tableWidgetFondsGeoservices.setHorizontalHeaderLabels(entete)
        self.tableWidgetFondsGeoservices.setColumnWidth(0, 400)
        self.tableWidgetFondsGeoservices.setColumnWidth(1, 200)
        self.tableWidgetFondsGeoservices.setColumnWidth(2, 130)

        # Autres lignes de la table
        for layer in self.__listLayers:
            if layer.type != cst.GEOSERVICE:
                continue

            rowPosition = self.tableWidgetFondsGeoservices.rowCount()
            self.tableWidgetFondsGeoservices.insertRow(rowPosition)

            # Colonne "Nom de la couche"
            item = QtWidgets.QTableWidgetItem(layer.geoservice['title'])
            self.tableWidgetFondsGeoservices.setItem(rowPosition, 0, item)

            # Colonne "Rôle"
            role = layer.role
            if role in self.roleCleVal:
                item = QtWidgets.QTableWidgetItem(self.roleCleVal[role])
            else:
                item = QtWidgets.QTableWidgetItem("Pas de rôle, bizarre !")
            self.tableWidgetFondsGeoservices.setItem(rowPosition, 1, item)

            # Colonne "Charger"
            self.__setColumnCharger(self.tableWidgetFondsGeoservices, rowPosition, 2)

    def __getLayersSelected(self, tableWidget, numCol) -> []:
        """
        :param tableWidget: la vue table des couches
        :type tableWidget: QTableWidget

        :param numCol: le numéro de la colonne
        :type numCol: int

        :return: la liste des layers sélectionnées par l'utilisateur en fonction des cases cochées
                 dans la colonne "Charger"
        """
        checked_list = []
        for i in range(tableWidget.rowCount()):
            item = tableWidget.item(i, numCol)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                itemCouche = tableWidget.item(i, 0)
                checked_list.append(itemCouche.text())
        return checked_list

    def __save(self) -> None:
        """
        L'utilisateur a cliqué sur le bouton Enregistrer pour lancer l'import des couches sélectionnées dans la carte.
        """
        self.accept()
        layersQGIS = []
        layersChecked = [self.__getLayersSelected(self.tableWidgetFondsGeoservices, 2),
                         self.__getLayersSelected(self.tableWidgetMonGuichet, 2)]
        # Par exemple[['adresse'], ['GEOGRAPHICALGRIDSYSTEMS.MAPS', 'GEOGRAPHICALGRIDSYSTEMS.PLANIGN'], [], []]
        for layerChecked in layersChecked:
            for tmp in layerChecked:
                for layer in self.__listLayers:
                    if tmp == layer.name():
                        layersQGIS.append(layer)
                        break
        # Téléchargement et import des couches du guichet sur la carte
        self.__doImport(layersQGIS)

    def __doImport(self, selectedLayers) -> None:
        """
        Import (addGuichetLayersToMap) des couches sélectionnées dans le projet en fonction du profil
        de l'utilisateur et de la zone de travail.

        :param selectedLayers: la liste des noms de couches sélectionnées par l'utilisateur
        :type selectedLayers: list
        """
        try:
            self.__logger.debug("doImport")

            if self.__context.getUserCommunity() is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            if self.__context.getUserCommunity().getName() is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            # Filtre spatial (la zone de travail)
            bbox = BBox(self.__context)
            box = bbox.getFromLayer(PluginHelper.load_CalqueFiltrage(self.__context.projectDir).text, False, True)
            # si la box est à None alors, l'utilisateur veut extraire France entière
            # si la box est égale 0.0 pour ces 4 coordonnées alors l'utilisateur
            # ne souhaite pas extraire les données France entière
            if box is not None and box.getXMax() == 0.0 and box.getYMax() == 0.0 \
                    and box.getXMin() == 0.0 and box.getYMin() == 0.0:
                return

            # Création de la table des tables
            SQLiteManager.createTableOfTables()

            # Import des couches du guichet sélectionnées par l'utilisateur
            self.__context.addGuichetLayersToMap(selectedLayers, box, self.__context.getUserCommunity().getName())

        except Exception as e:
            PluginHelper.showMessageBox('{}'.format(e))

    def __cancel(self) -> None:
        """
        L'utilisateur a cliqué sur la fermeture de la boite ou sur le bouton Annuler
        """
        self.reject()
        print("L'utilisateur est sorti de la boite : Charger les couches de mon groupe")
