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
from qgis.PyQt.QtWidgets import QMessageBox
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

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormConnection_base.ui'))


class FormConnectionDialog(QtWidgets.QDialog, FORM_CLASS):
    """ Fenêtre de login
    """
    context = None
    urlhost = ""
    projectDir = ""
    # bConnect = False
    # bCancel = True

    connectionResult = 0
    
    # logger
    logger = RipartLogger("FormConnexionDialog").getRipartLogger()
    
    def __init__(self, context, parent=None):
        """Constructor."""
        
        super(FormConnectionDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setContext(context)
        self.connectionResult = 0
#        self.textError.setVisible(False)

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

    def setLogin(self, login):
        self.lineEditLogin.setText(login)  
    
    def getLogin(self):
        return self.lineEditLogin.text()
    
    def getPwd(self):
        return self.lineEditPwd.text()


    def connectToService(self):
        """Connexion au service Espace collaboratif

        :return 1 si la connexion a réussi, 0 si elle a été annulée, -1 s'il y a eu une erreur (Exception)
        :rtype int
        """
        login = self.getLogin()

        self.context.login = self.getLogin()
        self.context.pwd = self.getPwd()
        print("login " + self.context.login)

        try:
            client = Client(self.urlhost, self.context.login, self.context.pwd, self.context.proxy)
            profil = client.getProfil()

            if profil is not None:
                RipartHelper.save_login(self.projectDir, login)
                self.context.client = client

                # si l'utilisateur appartient à 1 seul groupe, celui-ci est déjà actif
                # si l'utilisateur n'appartient à aucun groupe, un profil par défaut
                # est attribué mais il ne contient pas d'infosgeogroupes
                if len(profil.infosGeogroups) < 1:
                    # le profil de l'utilisateur est déjà récupéré et reste actif (NB: a priori, il n'a pas de profil)
                    self.context.profil = profil

                    # si l'utilisateur n'a pas de profil, il faut indiquer que le groupe actif est vide
                    if "défaut" in profil.title:
                        RipartHelper.save_groupeactif(self.projectDir, "Aucun")
                    else:
                        RipartHelper.save_groupeactif(self.projectDir, profil.geogroup.name)

                        # On enregistre le groupe comme groupe préféré (par défaut) pour la création de signalement
                        # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
                        preferredGroup = RipartHelper.load_preferredGroup(self.projectDir)
                        if preferredGroup != profil.geogroup.name:
                            RipartHelper.save_preferredThemes(self.projectDir, [])

                        RipartHelper.save_preferredGroup(self.projectDir, profil.geogroup.name)

                # sinon le choix d'un autre groupe est présenté à l'utilisateur
                # le formulaire est proposé même si l'utilisateur n'appartient qu'à un groupe
                # afin qu'il puisse remplir sa clé Géoportail
                else:
                    dlgChoixGroupe = FormChoixGroupe(self.context, profil, self.context.groupeactif)
                    dlgChoixGroupe.exec_()

                    # bouton Valider
                    if not dlgChoixGroupe.bCancel:

                        # le choix du nouveau profil est validé
                        # le nouvel id et nom du groupe sont retournés dans un tuple
                        idNomGroupe = dlgChoixGroupe.getChosenGroupInfo()

                        # si l'utilisateur n'appartient qu'à un seul gorupe, le profil chargé reste actif
                        if len(profil.infosGeogroups) == 1:
                            self.context.profil = profil
                        else:
                            # récupère le profil et un message dans un tuple
                            profilMessage = client.setChangeUserProfil(idNomGroupe[0])
                            messTmp = profilMessage[1]

                            # setChangeUserProfil retourne un message "Le profil du groupe xx est déjà actif"
                            if messTmp.find('actif') != -1:
                                # le profil chargé reste actif
                                self.context.profil = profil
                            else:
                                # setChangeUserProfil retourne un message vide
                                # le nouveau profil devient actif
                                self.context.profil = profilMessage[0]

                        # Sauvegarde du groupe actif dans le xml du projet utilisateur
                        RipartHelper.save_groupeactif(self.projectDir, idNomGroupe[1])
                        self.groupeactif = idNomGroupe[1]

                        # On enregistre le groupe comme groupe préféré pour la création de signalement
                        # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
                        formPreferredGroup = RipartHelper.load_preferredGroup(self.projectDir)
                        if formPreferredGroup != profil.geogroup.name:
                            RipartHelper.save_preferredThemes(self.projectDir, [])
                        RipartHelper.save_preferredGroup(self.projectDir, profil.geogroup.name)

                    # Bouton Annuler
                    elif dlgChoixGroupe.cancel:
                        print("rejected")
                        self.close()
                        self = None
                        return

                # les infos de connexion présentée à l'utilisateur
                dlgInfo = FormInfo()

                # Modification du logo en fonction du groupe
                if profil.logo != "":
                    logoPath = "{0}{1}".format(self.urlhost, profil.logo)
                    image = QImage()
                    image.loadFromData(requests.get(logoPath).content)
                    dlgInfo.logo.setPixmap(QtGui.QPixmap(image))
                elif profil.title == "Profil par défaut":
                    dlgInfo.logo.setPixmap(QtGui.QPixmap(":/plugins/RipartPlugin/images/logo_IGN.png"))

                dlgInfo.textInfo.setText(u"<b>Connexion réussie à l'Espace collaboratif</b>")
                dlgInfo.textInfo.append("<br/>Serveur : {}".format(self.urlhost))
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

                self.connectionResult = 1

            else:
                # fix_print_with_import
                print("error")

        except Exception as e:
            self.context.pwd = ""
            self.context.logger.error(format(e))
            self.context.client = None
            self.context.profil = None
            self.connectionResult = -1

            RipartHelper.showMessageBox(ClientHelper.notNoneValue(format(e)))

        return self.connectionResult

    def setContext(self, context):
        """Set du contexte
        """
        self.context = context
        self.lineEditLogin.setText(context.login)
        self.lineEditPwd.setText("")
        self.setUrlHost(context.urlHostRipart)
        self.setProjectDir(context.projectDir)

    def setUrlHost(self, urlhost):
        """Set de l'url du service Espace collaboratif
        """
        self.urlhost = urlhost

    def setProjectDir(self, projectDir):
        """Set de le chemin du projet QGIS
        """
        self.projectDir = projectDir

    def Cancel(self):
        self.close()

    def closeEvent(self, event):
        self.connectionResult = 0
        self.close()