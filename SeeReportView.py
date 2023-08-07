import os

from PyQt5 import QtCore
from qgis.PyQt import uic, QtWidgets
from numpy import double

from .core.Wkt import Wkt
from .core.RipartLoggerCl import RipartLogger
from .core import Constantes as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'SeeReportView_base.ui'))


class SeeReportView(QtWidgets.QDialog, FORM_CLASS):
    """
    Forme de visualisation de l'historique de la remarque + sélection/déselection croquis + ouverture document joint
    """
    def __init__(self, activeCommunityName) -> None:
        super(SeeReportView, self).__init__(None)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.__logger = RipartLogger("SeeReportView").getRipartLogger()
        self.__report = None
        self.__activeCommunityName = activeCommunityName

    def setReport(self, report) -> None:
        try:
            self.__report = report
            self.lbl_contentNumberReport.setText("Signalement n°{0}".format(report.getId()))
            self.lbl_contentNumberReport.setStyleSheet("QLabel {color : blue}")  # #ff0000
            self.lbl_displayGeneralInformation.setText(self.DisplayGeneralInformation())
            # self.pte_displayThemes.setPlainText(self.DisplayThemes())
            self.pte_displayThemes.setPlainText(report.getThemes())
            self.lbl_displayDescription.setText(report.getComment())
            self.DisplayFilesAttached()
            self.pte_displayResponses.setPlainText(report.concatenateReplies())
        except Exception as e:
            self.__logger.error("setRemarque")
            raise e

    def DisplayGeneralInformation(self) -> str:
        generalInformation = "Communauté : {0}\n".format(self.__activeCommunityName)
        generalInformation += "Auteur : {0}\n".format(self.__report.getAuthor())
        generalInformation += "Commune : {0}\n".format(self.DisplayTown(self.__report.getCommune(),
                                                                        self.__report.getInsee()))
        generalInformation += "Posté le : {0}\n".format(self.__report.getDateCreation())
        generalInformation += "Statut : {0}\n".format(self.DisplayStatus(self.__report.getStatut()))
        generalInformation += "Source : {0}\n".format(self.DisplaySource(self.__report.getInputDevice()))
        lonlat = Wkt.toGetLonLatFromGeometry(self.__report.getGeometry())
        generalInformation += "Localisation : {0}\n".format(self.DisplayLocation(lonlat[0], lonlat[1]))
        return generalInformation

    def DisplayTown(self, town, number) -> str:
        return "{0} ({1})".format(town, number)

    def DisplayStatus(self, statusToSearch) -> str:
        correspondance = {
            cst.STATUT.submit.__str__(): "Reçu dans nos services",
            cst.STATUT.pending.__str__(): "En cours de traitement",
            cst.STATUT.pending0.__str__(): "Demande de qualification",
            cst.STATUT.pending1.__str__(): "En attente de saisie",
            cst.STATUT.valid.__str__(): "Pris en compte",
            cst.STATUT.valid0.__str__(): "Déjà pris en compte",
            cst.STATUT.reject.__str__(): "Rejeté (hors spéc.)",
            cst.STATUT.reject0.__str__(): "Rejeté (hors de propos)",
            cst.STATUT.pending2.__str__(): "En attente de validation"
        }
        if statusToSearch in correspondance.keys():
            return correspondance[statusToSearch]
        else:
            return "Indéfini"

    def DisplaySource(self, stringToSearch) -> str:
        sources = {
            "UNKNOWN": "Soumise via l\'API",
            "www": "Saisie sur le site web",
            "SIG-GC": "Saisie depuis GeoConcept",
            "SIG-AG": "Saisie depuis ArcGIS",
            "SIG-QGIS": "Saisie depuis QGIS",
            "PHONE": "Saisie depuis un smartphone",
            "SPOTIT": "Saisie sur SPOTIT"
        }
        return sources[stringToSearch]

    def DisplayLocation(self, longitude, latitude) -> str:
        dirLon = "E"
        dirLat = "N"
        if longitude < 0:
            dirLon = "O"
        if latitude < 0:
            dirLat = "S"
        return "{0}°{1}, {2}°{3}".format(str(longitude), dirLon, str(latitude), dirLat)

    def DisplayThemes(self) -> str:
        displayThemes = ''
        themes = self.__report.concatenateThemes(False)
        for theme in themes:
            firstSeparator = {"|", ")"}
            for ch in firstSeparator:
                theme = theme.replace(ch, "\n")
            secondSeparator = {"(", ","}
            for ch in secondSeparator:
                theme = theme.replace(ch, "\n    ")
            displayThemes += theme
        return displayThemes.replace("=", " : ")

    def DisplayFilesAttached(self) -> None:
        allDocuments = self.__report.getAttachments()
        for document in allDocuments:
            self.lbl_displayDocuments.setText('<a href={0}>{1}</a>'.format(document, document))
            self.lbl_displayDocuments.setTextFormat(QtCore.Qt.TextFormat.RichText)
            self.lbl_displayDocuments.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
