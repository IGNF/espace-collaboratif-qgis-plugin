import os

from qgis.PyQt import uic
from PyQt5 import QtCore, QtWidgets
from qgis.PyQt.QtGui import QIcon, QColor

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ConflictsView_base.ui'))


class ConflictsView(QtWidgets.QDialog, FORM_CLASS):
    """
    Dialogue de gestion des conflits d'une carte
    """
    def __init__(self, context, parent=None) -> None:
        super(ConflictsView, self).__init__(parent)
        self.__context = context
        self.__getConflicts()
        self.__initDialog()

    def __getConflicts(self):
        a=1

    def __initDialog(self):
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        nb = self.__layerConflits.featureCount()
        if nb >= 1:
            self.setWindowTitle("Gestion des conflits - {} conflit(s)".format(nb))
        self.__initTableWidget()
        self.__setConnectButtons()
        self.__setImagesOnButtons()

    def __initTableWidget(self):
        entete = ["Nom des champs", "Objet issu du serveur", "Votre objet", "Commentaire"]
        self.tableWidget_attributes.setHorizontalHeaderLabels(entete)
        self.tableWidget_attributes.setColumnWidth(0, 190)
        self.tableWidget_attributes.setColumnWidth(1, 300)
        self.tableWidget_attributes.setColumnWidth(2, 300)
        self.tableWidget_attributes.setColumnWidth(3, 190)
        self.__setAttributesTableWidget()

    def __resetTableWidget(self):
        self.tableWidget_attributes.clear()
        self.tableWidget_attributes.setRowCount(0)

    def setColorItem(self):
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

    def __setAttributesTableWidget(self):
        a=1

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
        icon.addFile(":/plugins/RipartPlugin/images/conflict_previous.png")
        self.pushButton_conflict_previous.setIcon(icon)
        icon.addFile(":/plugins/RipartPlugin/images/conflict_next.png")
        self.pushButton_conflict_next.setIcon(icon)
        icon.addFile(":/plugins/RipartPlugin/images/conflict_see_all_fields.png")
        self.pushButton_conflict_see_all_fields.setIcon(icon)
        icon.addFile(":/plugins/RipartPlugin/images/conflict_reload.png")
        self.pushButton_conflict_reload.setIcon(icon)
        icon.addFile(":/plugins/RipartPlugin/images/conflict_create.png")
        self.pushButton_conflict_create.setIcon(icon)
        icon.addFile(":/plugins/RipartPlugin/images/conflict_delete.png")
        self.pushButton_conflict_delete.setIcon(icon)
        icon.addFile(":/plugins/RipartPlugin/images/conflict_validate.png")
        self.pushButton_conflict_validate.setIcon(icon)
        icon.addFile(":/plugins/RipartPlugin/images/conflict_validate_all.png")
        self.pushButton_conflict_validate_all.setIcon(icon)
        icon.addFile(":/plugins/RipartPlugin/images/conflict_undo.png")
        self.pushButton_conflict_undo.setIcon(icon)

