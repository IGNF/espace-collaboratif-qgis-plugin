import os
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

    def __init__(self, context, datas, nbConflicts, parent=None) -> None:
        super(ConflictsView, self).__init__(parent)
        self.setupUi(self)
        self.__context = context
        self.__getConflicts()
        self.__initDialog(nbConflicts)
        self.__datas = datas

    def __getConflicts(self):
        a=1

    def __initDialog(self, nbConflicts):
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        if nbConflicts >= 1:
            self.setWindowTitle("Gestion des conflits - {} conflit(s)".format(nbConflicts))
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

    def __createReport(self):
        PluginHelper.showMessageBox("createReport")

    def __previous(self):
        PluginHelper.showMessageBox("previous")

    def __next(self):
        PluginHelper.showMessageBox("next")

    def __seeAllFields(self):
        PluginHelper.showMessageBox("seeAllFields")

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
