import os
from PyQt5 import QtCore
from qgis.PyQt import uic, QtWidgets
from .core.Wkt import Wkt
from .core.RipartLoggerCl import RipartLogger
from .core import Constantes as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'SeeReportView_base.ui'))


class SeeReportView(QtWidgets.QDialog, FORM_CLASS):
    """
    Forme de visualisation de l'historique de la remarque + sélection/déselection croquis + ouverture document joint
    """
    def __init__(self, activeUserCommunity) -> None:
        super(SeeReportView, self).__init__(None)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.__logger = RipartLogger("SeeReportView").getRipartLogger()
        self.__report = None
        self.__activeUserCommunity = activeUserCommunity

    def setReport(self, report) -> None:
        try:
            self.__report = report
            self.lbl_contentNumberReport.setText("Signalement n°{0}".format(report.getId()))
            self.lbl_contentNumberReport.setStyleSheet("QLabel {color : blue}")  # #ff0000
            self.lbl_displayGeneralInformation.setText(self.__displayGeneralInformation())
            self.pte_displayThemes.setPlainText(self.__displayThemes())
            # TODO changer l'item description et documents joints de label en plain text
            self.lbl_displayDescription.setText(report.getMessage())
            self.__displayFilesAttached()
            self.pte_displayResponses.setPlainText(report.getStrReplies())
        except Exception as e:
            self.__logger.error("setReport")
            raise e

    def __displayGeneralInformation(self) -> str:
        generalInformation = "Groupe : {0}\n".format(self.__activeUserCommunity.getName())
        # TODO -> sur le guichet pour l'affichage d'un signalement sur l'auteur il y a un (ign.fr)
        # doit-on le déduire de l'adresse mail ?
        generalInformation += "Auteur : {0}\n".format(self.__report.getStrAuthor())
        generalInformation += "Commune : {0}\n".format(self.__displayTown())
        generalInformation += "Posté le : {0}\n".format(self.__report.getStrDateCreation())
        generalInformation += "Statut : {0}\n".format(self.__displayStatus())
        generalInformation += "Source : {0}\n".format(self.__displaySource())
        generalInformation += "Localisation : {0}\n".format(self.__displayLocation())
        return generalInformation

    def __displayTown(self) -> str:
        return "{0} ({1})".format(self.__report.getCommune(), self.__report.getInsee())

    def __displayStatus(self) -> str:
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
        if self.__report.getStatut() in correspondance.keys():
            return correspondance[self.__report.getStatut()]
        return "Indéfini"

    def __displaySource(self) -> str:
        sources = {
            "UNKNOWN": "Soumise via l\'API",
            "www": "Saisie sur le site web",
            "SIG-GC": "Saisie depuis GeoConcept",
            "SIG-AG": "Saisie depuis ArcGIS",
            "SIG-QGIS": "Saisie depuis QGIS",
            "PHONE": "Saisie depuis un smartphone",
            "SPOTIT": "Saisie sur SPOTIT"
        }
        if self.__report.getInputDevice() in sources.keys():
            return sources[self.__report.getInputDevice()]
        return "Indéfini"

    def __displayLocation(self) -> str:
        lonlat = Wkt.toGetLonLatFromGeometry(self.__report.getGeometry())
        dirLon = "E"
        dirLat = "N"
        if lonlat[0] < 0:
            dirLon = "O"
        if lonlat[1] < 0:
            dirLat = "S"
        return "{0}°{1}, {2}°{3}".format(str(lonlat[0]), dirLon, str(lonlat[1]), dirLat)

    def __displayThemes(self) -> str:
        displayThemes = ''
        themes = self.__report.getStrThemesForDisplay(self.__activeUserCommunity)
        for theme in themes:
            firstSeparator = {"|", ")"}
            for ch in firstSeparator:
                theme = theme.replace(ch, "\n")
            secondSeparator = {"(", ","}
            for ch in secondSeparator:
                theme = theme.replace(ch, "\n    ")
            displayThemes += theme
        return displayThemes.replace("=", " : ")

    def __displayFilesAttached(self) -> None:
        allDocuments = self.__report.getListAttachments()
        htmlDocuments = ''
        for document in allDocuments:
            htmlDocuments += '<a href={0}>{1}</a><br />'.format(document, document)
        self.lbl_displayDocuments.setText(htmlDocuments)
        self.lbl_displayDocuments.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.lbl_displayDocuments.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
