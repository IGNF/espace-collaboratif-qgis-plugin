# -*- coding: utf-8 -*-
"""
Created on 20 oct. 2015
Updated on 23 oct. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse
"""

import os

from PyQt5.QtWidgets import QDialogButtonBox
from qgis.PyQt import uic
from .core.RipartLoggerCl import RipartLogger
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage

import requests

from .core.Client import Client
from .core.ClientHelper import ClientHelper
from .RipartHelper import RipartHelper
from .FormChoixGroupe import FormChoixGroupe
from .FormInfo import FormInfo
from .core import ConstanteRipart as cst
from .core.Community import Community

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormConnection_base.ui'))


class FormConnectionDialog(QtWidgets.QDialog, FORM_CLASS):
    """ Fenêtre de login
    """

    def __init__(self, context, parent=None):
        super(FormConnectionDialog, self).__init__(parent)

        self.setupUi(self)
        self.connectionResult = 0
        self.urlHost = ""
        self.projectDir = ""
        self.setContext(context)
        # Quelques mises en forme du dialogue à son initialisation
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Connecter")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.connectToService)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.Cancel)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lblPwd.setFont(font)
        self.lblLogin.setFont(font)
        self.setStyleSheet("QDialog {background-color: rgb(255, 255, 255)}")
        self.setFixedSize(self.width(), self.height())

        # Initialisation du fichier de log
        self.logger = RipartLogger("FormConnexionDialog").getRipartLogger()

    def setLogin(self, login):
        self.lineEditLogin.setText(login)

    def getLogin(self):
        return self.lineEditLogin.text()

    def getPwd(self):
        return self.lineEditPwd.text()

    def setDisplayInformations(self, profile):
        # Les infos de connexion présentée à l'utilisateur
        dlgInfo = FormInfo()
        # Modification du logo en fonction du groupe
        if profile.logo != "":
            logoPath = "{0}{1}".format(self.urlHost, profile.logo)
            image = QImage()
            image.loadFromData(requests.get(logoPath).content)
            dlgInfo.logo.setPixmap(QtGui.QPixmap(image))
        elif profile.title == "Profil par défaut":
            dlgInfo.logo.setPixmap(QtGui.QPixmap(":/plugins/RipartPlugin/images/logo_IGN.png"))
        dlgInfo.textInfo.setText(u"<b>Connexion réussie à l'Espace collaboratif</b>")
        dlgInfo.textInfo.append("<br/>Serveur : {}".format(self.urlHost))
        dlgInfo.textInfo.append("Login : {}".format(self.context.login))
        dlgInfo.textInfo.append("Groupe : {}".format(self.context.profil.title))
        if self.context.profil.zone == cst.ZoneGeographique.UNDEFINED:
            zoneExtraction = RipartHelper.load_CalqueFiltrage(self.projectDir).text
            if zoneExtraction == "" or zoneExtraction is None or len(
                    self.context.QgsProject.instance().mapLayersByName(zoneExtraction)) == 0:
                dlgInfo.textInfo.append("Zone : pas de zone définie")
                RipartHelper.setXmlTagValue(self.projectDir, RipartHelper.xml_Zone_extraction, "", "Map")
            else:
                dlgInfo.textInfo.append("Zone : {}".format(zoneExtraction))
            self.context.profil.zone = zoneExtraction
        else:
            dlgInfo.textInfo.append("Zone : {}".format(self.context.profil.zone.__str__()))
        dlgInfo.exec_()

    def connectToService(self):
        # Sauvegarde des éléments de connexion
        self.context.login = self.getLogin()
        self.context.pwd = self.getPwd()
        community = Community(self.urlHost, self.context.login, self.context.pwd, self.context.proxy)
        try:
            listGroup = community.extractCommunities()
            RipartHelper.save_login(self.projectDir, self.getLogin())
            dlgChoixGroupe = FormChoixGroupe(self.context, listGroup, self.context.groupeactif)
            dlgChoixGroupe.exec_()
            if dlgChoixGroupe.cancel:
                dlgChoixGroupe.close()
                return
            else:
                # Le choix du nouveau profil est validé
                # Le nouvel id et nom du groupe sont retournés par un tuple
                idNomGroupe = dlgChoixGroupe.getChosenGroupInfo()
                self.context.profil = community.getUserProfil(idNomGroupe[0])

                # Sauvegarde du groupe actif dans le xml du projet utilisateur
                RipartHelper.save_groupeactif(self.projectDir, idNomGroupe[1])
                self.context.groupeactif = idNomGroupe[1]

                # On enregistre le groupe comme groupe préféré pour la création de signalement
                # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
                formPreferredGroup = RipartHelper.load_preferredGroup(self.projectDir)
                if formPreferredGroup != idNomGroupe[1]:
                    RipartHelper.save_preferredThemes(self.projectDir, [])
                RipartHelper.save_preferredGroup(self.projectDir, idNomGroupe[1])
                # Les informations de connexion sont montrées à l'utilisateur
                self.displayInformations()
            self.connectionResult = 1
        except Exception as e:
            self.context.pwd = ""
            self.context.logger.error(format(e))
            self.context.client = None
            self.context.profil = None
            self.connectionResult = -1
            RipartHelper.showMessageBox(ClientHelper.notNoneValue(format(e)))

        return self.connectionResult

    # def connectToService(self):
    #     """Connexion à l'Espace collaboratif
    #
    #     :return 1 si la connexion a réussi, 0 si elle a été annulée, -1 s'il y a eu une erreur (Exception)
    #     :rtype int
    #     """
    #     self.context.login = self.getLogin()
    #     self.context.pwd = self.getPwd()
    #     print("login " + self.context.login)
    #     try:
    #         client = Client(self.urlHost, self.context.login, self.context.pwd, self.context.proxy)
    #         profile = client.getProfile()
    #
    #         if profile is not None:
    #             RipartHelper.save_login(self.projectDir, self.getLogin())
    #             self.context.client = client
    #
    #             # si l'utilisateur appartient à 1 seul groupe, celui-ci est déjà actif
    #             # si l'utilisateur n'appartient à aucun groupe, un profil par défaut
    #             # est attribué mais il ne contient pas d'infosgeogroupes
    #             if len(profile.infosGeogroups) < 1:
    #                 # le profil de l'utilisateur est déjà récupéré et reste actif (NB: a priori, il n'a pas de profil)
    #                 self.context.profil = profile
    #
    #                 # si l'utilisateur n'a pas de profil, il faut indiquer que le groupe actif est vide
    #                 if "défaut" in profile.title:
    #                     RipartHelper.save_groupeactif(self.projectDir, "Aucun")
    #                 else:
    #                     RipartHelper.save_groupeactif(self.projectDir, profile.geogroup.name)
    #
    #                     # On enregistre le groupe comme groupe préféré (par défaut) pour la création de signalement
    #                     # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
    #                     preferredGroup = RipartHelper.load_preferredGroup(self.projectDir)
    #                     if preferredGroup != profile.geogroup.name:
    #                         RipartHelper.save_preferredThemes(self.projectDir, [])
    #
    #                     RipartHelper.save_preferredGroup(self.projectDir, profile.geogroup.name)
    #
    #             # sinon le choix d'un autre groupe est présenté à l'utilisateur
    #             # le formulaire est proposé même si l'utilisateur n'appartient qu'à un groupe
    #             # afin qu'il puisse remplir sa clé Géoportail
    #             else:
    #                 dlgChoixGroupe = FormChoixGroupe(self.context, profile, self.context.groupeactif)
    #                 dlgChoixGroupe.exec_()
    #
    #                 # bouton Valider
    #                 if not dlgChoixGroupe.bCancel:
    #
    #                     # le choix du nouveau profil est validé
    #                     # le nouvel id et nom du groupe sont retournés dans un tuple
    #                     idNomGroupe = dlgChoixGroupe.getChosenGroupInfo()
    #
    #                     # si l'utilisateur n'appartient qu'à un seul groupe, le profil chargé reste actif
    #                     if len(profile.infosGeogroups) == 1:
    #                         self.context.profil = profile
    #                     else:
    #                         profil = client.setChangeUserProfil(idNomGroupe[0])
    #                         self.context.profil = profil
    #                         # récupère le profil et un message dans un tuple
    #                         # profilMessage = client.setChangeUserProfil(idNomGroupe[0])
    #                         # messTmp = profilMessage[1]
    #                         #
    #                         # # setChangeUserProfil retourne un message "Le profil du groupe xx est déjà actif"
    #                         # if messTmp.find('actif') != -1:
    #                         #     # le profil chargé reste actif
    #                         #     self.context.profil = profil
    #                         # else:
    #                         #     # setChangeUserProfil retourne un message vide
    #                         #     # le nouveau profil devient actif
    #                         #     self.context.profil = profilMessage[0]
    #
    #                     # Sauvegarde du groupe actif dans le xml du projet utilisateur
    #                     RipartHelper.save_groupeactif(self.projectDir, idNomGroupe[1])
    #                     self.groupeactif = idNomGroupe[1]
    #
    #                     # On enregistre le groupe comme groupe préféré pour la création de signalement
    #                     # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
    #                     formPreferredGroup = RipartHelper.load_preferredGroup(self.projectDir)
    #                     if formPreferredGroup != profile.geogroup.name:
    #                         RipartHelper.save_preferredThemes(self.projectDir, [])
    #                     RipartHelper.save_preferredGroup(self.projectDir, profile.geogroup.name)
    #
    #                 # Bouton Annuler
    #                 elif dlgChoixGroupe.cancel:
    #                     print("rejected")
    #                     dlgChoixGroupe.close()
    #                     #self.close()
    #                     #self = None
    #                     return
    #
    #             # les infos de connexion présentée à l'utilisateur
    #             dlgInfo = FormInfo()
    #
    #             # Modification du logo en fonction du groupe
    #             if profile.logo != "":
    #                 logoPath = "{0}{1}".format(self.urlHost, profile.logo)
    #                 image = QImage()
    #                 image.loadFromData(requests.get(logoPath).content)
    #                 dlgInfo.logo.setPixmap(QtGui.QPixmap(image))
    #             elif profile.title == "Profil par défaut":
    #                 dlgInfo.logo.setPixmap(QtGui.QPixmap(":/plugins/RipartPlugin/images/logo_IGN.png"))
    #
    #             dlgInfo.textInfo.setText(u"<b>Connexion réussie à l'Espace collaboratif</b>")
    #             dlgInfo.textInfo.append("<br/>Serveur : {}".format(self.urlHost))
    #             dlgInfo.textInfo.append("Login : {}".format(self.context.login))
    #             dlgInfo.textInfo.append("Groupe : {}".format(self.context.profil.title))
    #             if self.context.profil.zone == cst.ZoneGeographique.UNDEFINED:
    #                 zoneExtraction = RipartHelper.load_CalqueFiltrage(self.projectDir).text
    #                 if zoneExtraction == "" or zoneExtraction is None or len(
    #                         self.context.QgsProject.instance().mapLayersByName(zoneExtraction)) == 0:
    #                     dlgInfo.textInfo.append("Zone : pas de zone définie")
    #                     RipartHelper.setXmlTagValue(self.projectDir, RipartHelper.xml_Zone_extraction, "", "Map")
    #                 else:
    #                     dlgInfo.textInfo.append("Zone : {}".format(zoneExtraction))
    #                 self.context.profil.zone = zoneExtraction
    #             else:
    #                 dlgInfo.textInfo.append("Zone : {}".format(self.context.profil.zone.__str__()))
    #
    #             dlgInfo.exec_()
    #
    #             self.connectionResult = 1
    #
    #         else:
    #             # fix_print_with_import
    #             print("error")
    #
    #     except Exception as e:
    #         self.context.pwd = ""
    #         self.context.logger.error(format(e))
    #         self.context.client = None
    #         self.context.profil = None
    #         self.connectionResult = -1
    #
    #         RipartHelper.showMessageBox(ClientHelper.notNoneValue(format(e)))
    #
    #     return self.connectionResult

    def setContext(self, context):
        """Set du contexte
        """
        self.context = context
        self.lineEditLogin.setText(context.login)
        self.lineEditPwd.setText("")
        self.setUrlHost(context.urlHostEspaceCo)
        self.setProjectDir(context.projectDir)

    def setUrlHost(self, urlHost):
        """Set de l'url du service Espace collaboratif
        """
        self.urlHost = urlHost

    def setProjectDir(self, projectDir):
        """Set de le chemin du projet QGIS
        """
        self.projectDir = projectDir

    def Cancel(self):
        self.close()

    def closeEvent(self, event):
        self.connectionResult = 0
        self.close()
