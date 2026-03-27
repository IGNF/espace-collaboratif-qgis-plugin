import json
import os
from .core import Constantes as cst
from qgis.PyQt import uic
from PyQt5 import QtCore, QtWidgets
from qgis.PyQt.QtGui import QIcon, QColor
from .PluginHelper import PluginHelper

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ConflictsView_base.ui'))


class ConflictsView(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue de gestion des conflits d'une carte
    """
    __datas = {}

    def __init__(self, context, featuresConflicts, parent=None) -> None:
        super(ConflictsView, self).__init__(parent)
        self.setupUi(self)
        self.__context = context
        self.__features = featuresConflicts
        self.__nbConflicts = len(featuresConflicts)
        self.__initDialog()
        # Filtrer les attributs (True = filtré)
        self.__filterActive = True

    def __initDialog(self):
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        if self.__nbConflicts >= 1:
            self.setWindowTitle("Gestion des conflits - {} conflit(s)".format(self.__nbConflicts))
        self.__initTableWidget()
        self.__setConnectButtons()
        self.__setImagesOnButtons()

    def __initTableWidget(self):
        entete = ["Nom des champs", "Objet issu du serveur", "Votre objet", "Commentaire"]
        self.tableWidget_attributes.setHorizontalHeaderLabels(entete)
        self.tableWidget_attributes.setColumnWidth(0, 180)
        self.tableWidget_attributes.setColumnWidth(1, 290)
        self.tableWidget_attributes.setColumnWidth(2, 290)
        self.tableWidget_attributes.setColumnWidth(3, 150)
        self.__setTableWidget()

    def __resetTableWidget(self):
        self.tableWidget_attributes.clear()
        self.tableWidget_attributes.setRowCount(0)

    def __setTableWidget(self):
        for feature in self.__features:
            self.__setLabelsConflit(feature)
            self.__setAttributes(feature)

    def __setColorItem(self):
        for row in range(self.tableWidget_attributes.rowCount()):
            item = self.tableWidget_attributes.item(row, 3)  # colonne à vérifier
            if not item:
                continue
            val = item.text()
            if val == '<>':
                item.setForeground(QColor("red"))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            else:
                item.setForeground(QColor("black"))
                font = item.font()
                font.setBold(False)
                item.setFont(font)

    def __setLabelsConflit(self, feature):
        typeConflict = feature['type_conflict']
        self.label_type_conflict.setText(typeConflict)
        self.label_layer_name.setText(feature['layer_name'])
        if typeConflict == cst.CONFLICT_MODIFICATION:
            self.label_context_type_conflict.setText('Le même objet a été modifié par un autre utilisateur et par vous '
                                                     'même depuis la dernière transaction.')
        elif typeConflict == cst.CONFLICT_SUPPRESSION_SERVEUR:
            self.label_context_type_conflict.setText('Le même objet a été supprimé par un autre utilisateur et modifié '
                                                     'par vous depuis la dernière transaction.')
        elif typeConflict == cst.CONFLICT_SUPPRESSION_CLIENT:
            self.label_context_type_conflict.setText('Le même objet a été modifié par un autre utilisateur et supprimé '
                                                     'par vous même depuis la dernière transaction.')

    def __mergeDataServerAndClient(self, dict1, dict2):
        # Si un dict est None ou pas un dict, on le remplace par {}
        dict1 = dict1 or {}
        dict2 = dict2 or {}
        # Union des clés
        try:
            all_keys = sorted(dict1.keys() | dict2.keys())
        except TypeError:
            # Si les clés ne sont pas comparables entre elles → pas de tri
            all_keys = dict1.keys() | dict2.keys()
        resultat = {}
        for k in all_keys:
            v1 = dict1.get(k, "")
            v2 = dict2.get(k, "")
            if v1 == "" or v2 == "":
                status = "--"
            elif v1 != v2:
                status = "<>"
            else:
                status = "="
            resultat[k] = [v1, v2, status]
        return resultat

    def __setAttributes(self, feature):
        resultats = self.__mergeDataServerAndClient(json.loads(feature['data_server']),
                                                    json.loads(feature['data_client']))
        print("[INFO] Resultat : {}".format(resultats))

        for k, v in resultats.items():
            rowPosition = self.tableWidget_attributes.rowCount()
            self.tableWidget_attributes.insertRow(rowPosition)

            # Colonne "Nom des champs"
            item = QtWidgets.QTableWidgetItem(str(k))
            self.tableWidget_attributes.setItem(rowPosition, 0, item)

            # Colonne "Objet issu du serveur"
            item = QtWidgets.QTableWidgetItem(str(v[0]))
            self.tableWidget_attributes.setItem(rowPosition, 1, item)

            # Colonne "Votre objet"
            item = QtWidgets.QTableWidgetItem(str(v[1]))
            self.tableWidget_attributes.setItem(rowPosition, 2, item)

            # Colonne "Commentaire"
            item = QtWidgets.QTableWidgetItem(str(v[2]))
            self.tableWidget_attributes.setItem(rowPosition, 3, item)
        # Au départ, affichage uniquement des différences
        self.__showDiff()

    def __setConnectButtons(self):
        self.pushButton_conflict_create_report.clicked.connect(self.__createReport)
        self.pushButton_conflict_previous.clicked.connect(self.__previous)
        self.pushButton_conflict_next.clicked.connect(self.__next)
        self.pushButton_conflict_see_all_fields.clicked.connect(self.__seeAllFields)
        self.pushButton_conflict_reload.clicked.connect(self.__reload)
        self.pushButton_conflict_create.clicked.connect(self.__create)
        self.pushButton_conflict_delete.clicked.connect(self.__delete)
        self.pushButton_conflict_validate.clicked.connect(self.__validate)
        self.pushButton_conflict_validate_all.clicked.connect(self.__validateAll)
        self.pushButton_conflict_undo.clicked.connect(self.__undo)

    def __setImagesOnButtons(self):
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/create.png")
        self.pushButton_conflict_create_report.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_previous.png")
        self.pushButton_conflict_previous.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_next.png")
        self.pushButton_conflict_next.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_see_all_fields.png")
        self.pushButton_conflict_see_all_fields.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_reload.png")
        self.pushButton_conflict_reload.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_create.png")
        self.pushButton_conflict_create.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_delete.png")
        self.pushButton_conflict_delete.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_validate.png")
        self.pushButton_conflict_validate.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_validate_all.png")
        self.pushButton_conflict_validate_all.setIcon(icon)
        icon = QIcon()
        icon.addFile(":/plugins/RipartPlugin/images/conflict_undo.png")
        self.pushButton_conflict_undo.setIcon(icon)

    # -- 1) Créer un signalement --
    def __createReport(self):
        PluginHelper.showMessageBox("createReport")

    # -- 2) Aller au conflit précédent --
    def __previous(self):
        PluginHelper.showMessageBox("previous")

    # -- 3) Aller au conflit suivant --
    def __next(self):
        PluginHelper.showMessageBox("next")

    # -- 4) Filtrer les attributs --
    """Affiche toutes les lignes."""
    def __showAll(self):
        for row in range(self.tableWidget_attributes.rowCount()):
            self.tableWidget_attributes.setRowHidden(row, False)
        self.__setColorItem()

    """N'affiche que les lignes dont la valeur de la colonne testée est '<>'."""
    def __showDiff(self):
        for row in range(self.tableWidget_attributes.rowCount()):
            item = self.tableWidget_attributes.item(row, 3)
            if item is None or item.text() != "<>":
                self.tableWidget_attributes.setRowHidden(row, True)
            else:
                self.tableWidget_attributes.setRowHidden(row, False)

    """Alterner l'affichage entre attributs filtrés et non filtrés."""
    def __seeAllFields(self):
        if self.__filterActive:
            self.__showAll()
        else:
            self.__showDiff()
        # alterne l’état
        self.__filterActive = not self.__filterActive

    def __reload(self):
        PluginHelper.showMessageBox("reload")

    def __create(self):
        PluginHelper.showMessageBox("create")

    def __delete(self):
        PluginHelper.showMessageBox("delete")

    def __validate(self):
        PluginHelper.showMessageBox("validate")

    def __validateAll(self):
        PluginHelper.showMessageBox("validateAll")

    def __undo(self):
        PluginHelper.showMessageBox("undo")
