# -*- coding: utf-8 -*-
import os

from PyQt5 import QtCore
from numpy import double

from .core.RipartLoggerCl import RipartLogger
from qgis.PyQt import uic, QtWidgets
from .core import ConstanteRipart as cst

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'SeeReportView_base.ui'))

context = None


class SeeReportView(QtWidgets.QDialog, FORM_CLASS):
    """
    Forme de visualisation de l'historique de la remarque + sélection/déselection croquis + ouverture document joint
    """
    logger = RipartLogger("SeeReportView").getRipartLogger()

    def __init__(self, context, report):
        """
        Constructor
        """
        super(SeeReportView, self).__init__(None)
        self.setupUi(self)
        self.context = context
        self.report = report

    def setReport(self):
        try:
            self.lbl_contentNumberReport.setText("Signalement n°{0}".format(self.report.id))
            self.lbl_contentNumberReport.setStyleSheet("QLabel {color : blue}")  # #ff0000
            self.lbl_displayGeneralInformation.setText(self.DisplayGeneralInformation())
            self.pte_displayThemes.setPlainText(self.DisplayThemes())
            self.lbl_displayDescription.setText(self.report.commentaire)
            self.DisplayFilesAttached()
            self.pte_displayResponses.setPlainText(self.report.concatenateResponse())
        except Exception as e:
            self.logger.error("setRemarque")
            raise e

    def DisplayGeneralInformation(self):
        generalInformation = "Groupe : {0}\n".format(self.context.groupeactif)
        generalInformation += "Auteur : {0}\n".format(self.report.author.name)
        generalInformation += "Commune : {0}\n".format(self.DisplayTown(self.report.commune, self.report.insee))
        generalInformation += "Posté le : {0}\n".format(self.report.dateCreation)
        generalInformation += "Statut : {0}\n".format(self.DisplayStatus(self.report.statut))
        generalInformation += "Source : {0}\n".format(self.DisplaySource(self.report.source))
        generalInformation += "Localisation : {0}\n".format(
            self.DisplayLocation(self.report.position.longitude, self.report.position.latitude))
        return generalInformation

    def DisplayTown(self, town, number):
        return "{0} ({1})".format(town, number)

    def DisplayStatus(self, statusToSearch):
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

    def DisplaySource(self, stringToSearch):
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

    def DisplayLocation(self, longitude, latitude):
        lon = double(longitude)
        lat = double(latitude)
        dirLon = "E"
        dirLat = "N"
        if lon < 0:
            dirLon = "O"
        if lat < 0:
            dirLat = "S"
        return "{0}°{1}, {2}°{3}".format(longitude.replace("-", ""), dirLon, latitude.replace("-", ""), dirLat)

    def DisplayThemes(self):
        displayThemes = ''
        themes = self.report.concatenateThemes()
        for theme in themes:
            firstSeparator = {"|", ")"}
            for ch in firstSeparator:
                theme = theme.replace(ch, "\n")
            secondSeparator = {"(", ","}
            for ch in secondSeparator:
                theme = theme.replace(ch, "\n    ")
            displayThemes += theme
        return displayThemes.replace("=", " : ")

    def DisplayFilesAttached(self):
        allDocuments = self.report.getAllDocumentsForDisplay()
        for document in allDocuments:
            self.lbl_displayDocuments.setText('<a href={0}>{1}</a>'.format(document, document))
            self.lbl_displayDocuments.setTextFormat(QtCore.Qt.TextFormat.RichText)
            self.lbl_displayDocuments.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
