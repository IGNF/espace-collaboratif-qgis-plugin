import os
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5 import QtCore
from qgis.PyQt import uic, QtWidgets
from .PluginHelper import PluginHelper
from .core.BBox import BBox
from .core.NoProfileException import NoProfileException
from .core.SQLiteManager import SQLiteManager
from .core.RipartLoggerCl import RipartLogger
from .core import Constantes as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormChargerGuichet_base.ui'))


class FormChargerGuichet(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue pour afficher la liste des couches disponibles pour le profil utilisateur
    et récupération du choix de l'utilisateur
    """

    # Balises <ROLE>
    # Role de la couche dans le cadre d'un guichet
    # - visu = couche servant de fond uniquement
    # - ref = couche servant de référence pour la saisie (snapping ou routing)
    # - edit, ref-edit = couche éditable sur le guichet
    # "clé xml":"valeur affichage boite"
    roleCleVal = {"edit": "Edition", "ref-edit": "Edition", "visu": "Visualisation", "ref": "Visualisation"}

    bRejected = False

    def __init__(self, context, listLayers, parent=None) -> None:
        super(FormChargerGuichet, self).__init__(parent)
        self.setupUi(self)
        self.setFocus()
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.__context = context
        self.__logger = RipartLogger("ImporterGuichet").getRipartLogger()
        self.__listLayers = listLayers
        # Il faut inverser l'ordre pour retrouver le paramétrage de la carte du groupe
        self.__listLayers.reverse()

        # Remplissage des différentes tables de couches
        self.__setTableWidgetMonGuichet()
        self.__setTableWidgetFondsGeoservices()

        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.__save)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.__cancel)

        self.pushButton_checkAllBoxes_MonGuichet.clicked.connect(self.__checkAllBoxesMonGuichet)
        self.pushButton_checkAllBoxes_FondsGeoservices.clicked.connect(self.__checkAllBoxesFondsGeoservices)

        self.labelGroupeActif.setText("Communauté active : {}".format(context.getUserCommunity().getName()))
        self.labelGroupeActif.setStyleSheet("QLabel {color : blue}")  # #ff0000

    def __checkAllBoxesMonGuichet(self) -> None:
        for i in range(self.tableWidgetMonGuichet.rowCount()):
            item = self.tableWidgetMonGuichet.item(i, 2)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Checked)

    def __checkAllBoxesFondsGeoservices(self) -> None:
        for i in range(self.tableWidgetFondsGeoservices.rowCount()):
            item = self.tableWidgetFondsGeoservices.item(i, 2)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.CheckState.Checked)

    def __setColonneCharger(self, tableWidget, row, column, check=False) -> None:
        itemCheckBox = QtWidgets.QTableWidgetItem()
        itemCheckBox.setFlags(QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        if not check:
            itemCheckBox.setCheckState(QtCore.Qt.CheckState.Unchecked)
        else:
            itemCheckBox.setCheckState(QtCore.Qt.CheckState.Checked)
        tableWidget.setItem(row, column, itemCheckBox)

    def __setTableWidgetMonGuichet(self) -> None:
        # Entête
        entete = ["Nom de la couche", "Rôle", "Charger"]
        self.tableWidgetMonGuichet.setHorizontalHeaderLabels(entete)
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
            item = QtWidgets.QTableWidgetItem(layer.name)
            self.tableWidgetMonGuichet.setItem(rowPosition, 0, item)

            # Colonne "Rôle"
            role = layer.role
            if role in self.roleCleVal:
                item = QtWidgets.QTableWidgetItem(self.roleCleVal[role])
            else:
                item = QtWidgets.QTableWidgetItem("Pas de rôle, bizarre !")
            self.tableWidgetMonGuichet.setItem(rowPosition, 1, item)
            self.__setColonneCharger(self.tableWidgetMonGuichet, rowPosition, 2)

    def __setTableWidgetFondsGeoservices(self) -> None:
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
            self.__setColonneCharger(self.tableWidgetFondsGeoservices, rowPosition, 2)

    def __getLayersSelected(self, tableWidget, numCol) -> []:
        checked_list = []
        for i in range(tableWidget.rowCount()):
            item = tableWidget.item(i, numCol)
            if item.checkState() == QtCore.Qt.CheckState.Checked:
                itemCouche = tableWidget.item(i, 0)
                checked_list.append(itemCouche.text())
        return checked_list

    def __save(self) -> None:
        self.accept()
        layersQGIS = []
        layersChecked = [self.__getLayersSelected(self.tableWidgetFondsGeoservices, 2),
                         self.__getLayersSelected(self.tableWidgetMonGuichet, 2)]
        # Par exemple[['adresse'], ['GEOGRAPHICALGRIDSYSTEMS.MAPS', 'GEOGRAPHICALGRIDSYSTEMS.PLANIGN'], [], []]
        for layerChecked in layersChecked:
            for tmp in layerChecked:
                for layer in self.__listLayers:
                    if tmp == layer.name:
                        layersQGIS.append(layer)
                        break
        # Téléchargement et import des couches du guichet sur la carte
        self.__doImport(layersQGIS)

    def __doImport(self, selectedLayers) -> None:
        try:
            self.__logger.debug("doImport")

            if self.__context.getUserCommunity() is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            if self.__context.getUserCommunity().getName() is None:
                raise NoProfileException(
                    "Vous n'êtes pas autorisé à effectuer cette opération. Vous n'avez pas de profil actif.")

            # filtre spatial
            bbox = BBox(self.__context)
            box = bbox.getFromLayer(PluginHelper.load_CalqueFiltrage(self.__context.projectDir).text, False, True)
            # si la box est à None alors, l'utilisateur veut extraire France entière
            # si la box est égale 0.0 pour ces 4 coordonnées alors l'utilisateur
            # ne souhaite pas extraire les données France entière
            if box is not None and box.getXMax() == 0.0 and box.getYMax() == 0.0 \
                    and box.getXMin() == 0.0 and box.getYMin() == 0.0:
                return

            # création de la table des tables
            SQLiteManager.createTableOfTables()

            # Import des couches du guichet sélectionnées par l'utilisateur
            self.__context.addGuichetLayersToMap(selectedLayers, box, self.__context.getUserCommunity().getName())

        except Exception as e:
            PluginHelper.showMessageBox('{}'.format(e))

    def __cancel(self) -> None:
        self.reject()
        print("L'utilisateur est sorti de la boite : Charger les couches de mon groupe")
