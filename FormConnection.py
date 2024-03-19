import os
import requests
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QImage
from qgis.PyQt import uic
from .core.CommunitiesMember import CommunitiesMember
from .core.RipartLoggerCl import RipartLogger
from .core.ClientHelper import ClientHelper
from .PluginHelper import PluginHelper
from .FormChoixGroupe import FormChoixGroupe
from .FormInfo import FormInfo

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormConnection_base.ui'))


# Fenêtre de login
class FormConnectionDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, context, parent=None) -> None:
        super(FormConnectionDialog, self).__init__(parent)
        self.setupUi(self)
        self.__context = None
        self.__urlHost = ''
        self.__projectDir = ''
        self.__auth = {}
        # Par défaut -1 (problème de connection), si 1 connection réussie
        self.__connectionResult = -1
        self.__logger = RipartLogger("FormConnexionDialog").getRipartLogger()
        self.__setContextAndVariables(context)
        # Quelques mises en forme du dialogue avant affichage vers l'utilisateur
        self.__shapeDialog()

    def __setContextAndVariables(self, context) -> None:
        self.__context = context
        self.__urlHost = context.urlHostEspaceCo
        self.__projectDir = context.projectDir
        self.lineEditLogin.setText(context.login)
        self.lineEditPwd.setText("")

    def __shapeDialog(self) -> None:
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Connecter")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.__connectToService)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.Cancel)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lblPwd.setFont(font)
        self.lblLogin.setFont(font)
        self.setStyleSheet("QDialog {background-color: rgb(255, 255, 255)}")
        self.setFixedSize(self.width(), self.height())

    def getConnectionResult(self) -> int:
        return self.__connectionResult

    def getAuthentification(self) -> {}:
        return self.__auth

    def setLineEditLogin(self, login) -> None:
        self.lineEditLogin.setText(login)

    def getLineEditLogin(self) -> str:
        return self.lineEditLogin.text()

    def getLineEditPwd(self) :
        return self.lineEditPwd.text()

    # La fonction correspond au bouton Connecter...
    def __connectToService(self):
        self.__context.login = self.getLineEditLogin()
        self.__context.pwd = self.getLineEditPwd()
        if self.__context.login == '' or self.__context.pwd == '':
            self.__context.pwd = ""
            self.__context.client = None
            self.__context.profil = None
            self.__connectionResult = -1
            return self.__connectionResult
        # Sauvegarde des éléments de connexion
        self.__auth['login'] = self.getLineEditLogin()
        self.__auth['password'] = self.getLineEditPwd()
        PluginHelper.save_login(self.__projectDir, self.getLineEditLogin())
        try:
            # Recherche des communautés
            communities = CommunitiesMember(self.__urlHost, self.getLineEditLogin(), self.getLineEditPwd(),
                                            self.__context.proxy)
            communities.extractCommunities()
            self.__context.setCommunity(communities)
            # La liste des communautés à afficher dans la boite de choix des communautés
            self.__context.setListNameOfCommunities(communities.getListNameOfCommunities())
            self.__context.setUserNameCommunity(communities.getUserName())
            dlgSelectedCommunities = FormChoixGroupe(self.__context)
            dlgSelectedCommunities.exec_()
            # bouton Continuer (le choix du nouveau profil est validé)
            if not dlgSelectedCommunities.getCancel():
                # Le nouvel id et nom du groupe sont retournés dans un tuple idNameCommunity
                idNameCommunity = dlgSelectedCommunities.getIdAndNameFromSelectedCommunity()

                # La communauté de l'utilisateur est stocké dans le contexte
                self.__context.setUserCommunity(communities.getUserCommunity(idNameCommunity[1]))
                self.__context.setActiveCommunityName(idNameCommunity[1])

                # Sauvegarde du groupe actif dans le xml du projet utilisateur
                PluginHelper.saveActiveCommunityName(self.__projectDir, idNameCommunity[1])
                self.__context.setActiveCommunityName(idNameCommunity[1])

                # On enregistre le groupe comme groupe préféré pour la création de signalement
                # Si ce n'est pas le même qu'avant, on vide les thèmes préférés
                formPreferredGroup = PluginHelper.load_preferredGroup(self.__projectDir)
                if formPreferredGroup != idNameCommunity[1]:
                    # TODO voir avec Noémie, il s'agit bien des themes utilisateur (ceux dans community)
                    #  et non activeThemes ou shared_themes ?
                    PluginHelper.save_preferredThemes(self.__projectDir, self.__context.getUserCommunity().getTheme())
                PluginHelper.save_preferredGroup(self.__projectDir, idNameCommunity[1])
            # Bouton Annuler
            elif dlgSelectedCommunities.getCancel():
                dlgSelectedCommunities.close()
                self.close()
                return
            # Les informations de connexion sont montrées à l'utilisateur
            self.__setDisplayInformations()
            self.__connectionResult = 1
        except Exception as e:
            self.__context.logger.error(format(e))
            self.__context.pwd = ""
            self.__context.client = None
            self.__context.profil = None
            self.__connectionResult = -1
            PluginHelper.showMessageBox(ClientHelper.notNoneValue(format(e)))
        return self.__connectionResult

    def __setDisplayInformations(self):
        # Les infos de connexion présentée à l'utilisateur
        dlgInfo = FormInfo()
        # Modification du logo en fonction du groupe
        if self.__context.getUserCommunity().getLogo() != "":
            image = QImage()
            image.loadFromData(requests.get(self.__context.getUserCommunity().getLogo()).content)
            dlgInfo.logo.setPixmap(QtGui.QPixmap(image))
        elif self.__context.getUserCommunity().getName() == "Profil par défaut":
            dlgInfo.logo.setPixmap(QtGui.QPixmap(":/plugins/ign_espace_collaboratif_qgis/images/logo_IGN.png"))
        dlgInfo.textInfo.setText(u"<b>Connexion réussie à l'Espace collaboratif</b>")
        dlgInfo.textInfo.append("<br/>Serveur : {}".format(self.__urlHost))
        dlgInfo.textInfo.append("Login : {}".format(self.__context.login))
        dlgInfo.textInfo.append("Groupe : {}".format(self.__context.getUserCommunity().getName()))
        zoneExtraction = PluginHelper.load_CalqueFiltrage(self.__projectDir).text
        if zoneExtraction == "" or zoneExtraction is None or len(
                self.__context.QgsProject.instance().mapLayersByName(zoneExtraction)) == 0:
            dlgInfo.textInfo.append("Zone de travail : pas de zone définie")
            PluginHelper.setXmlTagValue(self.__projectDir, PluginHelper.xml_Zone_extraction, "", "Map")
        else:
            dlgInfo.textInfo.append("Zone de travail : {}".format(zoneExtraction))
        # TODO faut-il contrôler (mais de quelle manière ?) la zone de travail de l'utilisateur
        #  avec la variable emprises (FR, 38185, autre) de community qui autorise les droits de saisie
        #  sachant que nous n'avons pas pour l'instant l'emprise géographique stockée sur le serveur
        #  Faut-il indiquer l'emprise sur le serveur ? pour distinguer emprise serveur et zone de travail QGIS ?
        #  je l'ai ajouté dans le doute
        strEmprises = ''
        if len(self.__context.getUserCommunity().getEmprises()) == 0:
            strEmprises = 'aucune,'
        else:
            for emprise in self.__context.getUserCommunity().getEmprises():
                strEmprises += "{},".format(emprise)
        dlgInfo.textInfo.append("Emprise(s) serveur : {}".format(strEmprises[:-1]))
        # if self.__context.profil.zone == cst.ZoneGeographique.UNDEFINED:
        #     zoneExtraction = PluginHelper.load_CalqueFiltrage(self.__projectDir).text
        #     if zoneExtraction == "" or zoneExtraction is None or len(
        #             self.__context.QgsProject.instance().mapLayersByName(zoneExtraction)) == 0:
        #         dlgInfo.textInfo.append("Zone : pas de zone définie")
        #         PluginHelper.setXmlTagValue(self.__projectDir, PluginHelper.xml_Zone_extraction, "", "Map")
        #     else:
        #         dlgInfo.textInfo.append("Zone : {}".format(zoneExtraction))
        #     self.__context.profil.zone = zoneExtraction
        # else:
        #     dlgInfo.textInfo.append("Zone : {}".format(self.__context.profil.zone.__str__()))
        dlgInfo.exec_()

    def Cancel(self) -> None:
        self.close()

    def closeEvent(self, event) -> None:
        self.__connectionResult = 1
        self.close()
