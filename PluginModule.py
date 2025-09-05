import logging
import os.path
import configparser

from qgis.core import QgsFeatureRequest
# Initialize Qt resources from file resources.py
from . import resources
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from qgis.PyQt.QtWidgets import QAction, QMenu, QMessageBox, QToolButton, QApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayerEditBuffer
from builtins import str
from .core.BBox import BBox
from .core.WfsPost import WfsPost
from .core.PluginLogger import PluginLogger
from .core.SQLiteManager import SQLiteManager
from .core.WfsGet import WfsGet
from .core.ProgressBar import ProgressBar
from .core.Community import Community
from .core import Constantes as cst
from .Contexte import Contexte
from .FormChargerGuichet import FormChargerGuichet
from .FormInfo import FormInfo
from .FormConfigure import FormConfigure
from .ToolsReport import ToolsReport
from .SeeReport import SeeReport
from .CreateReport import CreateReport
from .Magicwand import Magicwand
from .PluginHelper import PluginHelper
from .ReplyReport import ReplyReport


# QGIS Plugin Implementation
class RipartPlugin:
    """
    Classe d'implémentation du plugin espace collaboratif (ex Ripart).
    """
    def __init__(self, iface) -> None:
        """
        Constructeur.

        :param iface: interface du plugin
        """
        self.toolButton2 = None
        self.helpMenu = None
        self.__context = Contexte.getInstance(self, QgsProject)
        self.__dlgConfigure = None
        self.__ripartLogger = PluginLogger("RipartPlugin")
        self.__logger = self.__ripartLogger.getPluginLogger()
        # Save reference to the QGIS interface
        self.iface = iface
        self.config = QAction(QIcon(":/plugins/RipartPlugin/images/config.png"), u"Configurer le plugin",
                              self.iface.mainWindow())
        self.help = QAction(QIcon(":/plugins/RipartPlugin/images/Book.png"), "Ouvrir le manuel utilisateur du plugin",
                            self.iface.mainWindow())
        self.log = QAction(QIcon(":/plugins/RipartPlugin/images/Log.png"), "Ouvrir le fichier de log du plugin",
                           self.iface.mainWindow())
        self.about = QAction(QIcon(":/plugins/RipartPlugin/images/About.png"), "A propos du plugin",
                             self.iface.mainWindow())

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RipartPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # La toolbar du plugin
        self.actions = []
        self.menu = self.__translate(u'&IGN_Espace_Collaboratif')
        self.toolbar = self.iface.addToolBar(u'RipartPlugin')
        self.toolbar.setObjectName(u'RipartPlugin')

        # En fin de chargement du projet ou à l'ajout d'une couche, il y a connexion de signaux
        # - quand le nom de la couche est changé
        # - quand des mises à jour ont été effectuées sur la couche
        self.iface.projectRead.connect(self.__connectProjectRead)
        QgsProject.instance().layerWasAdded.connect(self.__connectLayerWasAdded)
        QgsProject.instance().layerRemoved.connect(self.__connectLayerRemoved)

    def __connectLayerRemoved(self, layerId) -> None:
        """
        Quand l'utilisateur détruit une couche en passant par QGIS, il faut détruire les tables dans la base
        SQLite du projet.

        :param layerId: l'identifiant de la couche QGIS
        :type layerId: str
        """
        layer = QgsProject.instance().mapLayer(layerId)
        # Attention la couche n'existe peut-être plus
        if layer is None:
            return
        SQLiteManager.emptyTable(layer.name())
        SQLiteManager.deleteTable(layer.name())
        SQLiteManager.vacuumDatabase()

    def __connectProjectRead(self) -> None:
        """
        Connexion de signaux spécifiques sur les couches utilisateurs qui appartiennent à un groupe préfixé "ESPACECO_"
        et qui ont été extraites avec le plugin. Les noms de ces couches se retrouvent dans la table des tables.
        dans la base SQLite.
        """
        # si le contexte n'est pas encore initialisé
        if self.__context is None:
            self.__context = Contexte.getInstance(self, QgsProject)

        # S'il y a une erreur au chargement du projet, le contexte n'est pas chargé, sortie de programme
        if self.__context is None:
            return

        if self.__context.projectDir == "":
            PluginHelper.showMessageBox(cst.PROJECT_NOREGISTERED)
            raise Exception(u"Projet QGIS non enregistré")

        # S'il n'a y pas de base SQLite
        uri = self.__context.getUriDatabaseSqlite()
        if uri is None:
            return

        # S'il n'y a pas de table des tables
        if not SQLiteManager.isTableExist(cst.TABLEOFTABLES):
            return

        if self.__context.urlHostEspaceCo is None or self.__context.urlHostEspaceCo == "":
            return

        root = QgsProject.instance().layerTreeRoot()
        nodesGroup = root.findGroups()
        for ng in nodesGroup:
            # Dans le cas ou le nom du groupe actif, du groupe dans la carte et celui stocké dans le xml sont tous
            # les trois différents et qu'il n'y a qu'un seul groupe [ESPACE CO] par construction, le plus simple
            # est de chercher le prefixe
            if ng.name().find(cst.ESPACECO) != -1 and self.__context.getUserCommunity() is None:
                message = "Votre projet contient des couches de l'Espace collaboratif IGN. Pour continuer à les " \
                          "utiliser, nous vous conseillons de vous y connecter.\nVoulez-vous vous connecter " \
                          "à l'Espace collaboratif ? "
                reply = QMessageBox.question(self.iface.mainWindow(), cst.IGNESPACECO, message, QMessageBox.Yes,
                                             QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.__context = Contexte.getInstance(self, QgsProject)
                    if self.__context is None:
                        return
                    if self.__context.getUserCommunity() is None:
                        self.__context.getConnexionEspaceCollaboratifWithKeycloak(True)
                elif reply == QMessageBox.No:
                    projectLayers = QgsProject.instance().mapLayers()
                    for k, v in projectLayers.items():
                        if not self.__searchSpecificLayerInSQLite(v.name()):
                            continue
                        self.__connectSpecificSignals(v)
            break

        # TODO voir avec Mélanie
        # Est-ce que la base SQLite est désynchronisée avec le project ?
        # La liste des layers du projet se retrouve bien dans la table des tables pour la base SQLite ?
        # self.__doSynchroWithTableOfTables()

        # TODO voir avec Mélanie
        # S'il reste des objets non envoyés sur l'espace collaboratif
        # objectsAddedNotCommitted = self.__isObjectsAddedNotCommitted()
        # if len(objectsAddedNotCommitted) >= 1:
        #     message = "Votre projet contient des objets non synchronisés avec l'Espace collaboratif IGN. Nous vous " \
        #               "conseillons de les synchroniser sur le serveur.\nVoulez-vous le faire ? "
        #     reply = QMessageBox.question(self.iface.mainWindow(), cst.IGNESPACECO, message, QMessageBox.Yes,
        #                                  QMessageBox.No)
        #     if reply == QMessageBox.Yes:
        #         for objectAddedNotCommitted in objectsAddedNotCommitted:
        #             qgsVectorLayerEditBuffer = QgsVectorLayerEditBuffer(objectAddedNotCommitted[0])
        #             qgsVectorLayerEditBuffer.addFeature(objectAddedNotCommitted[1])
        #             messages = self.__doPost(objectAddedNotCommitted[0], qgsVectorLayerEditBuffer)
        #         return

    def __connectLayerWasAdded(self, layer) -> None:
        """
        Si une couche est ajoutée au projet QGIS de l'utilisateur et qu'elle se trouve dans la table des tables
        dans SQLite (ce qui veut dire que l'utilisateur a extrait cette couche par l'outil) alors la connexion
        des signaux spécifiques est possible.

        :param layer: la couche qui vient d'être ajoutée
        :type layer: QgsMapLayer
        """
        if layer is None:
            return
        if not self.__searchSpecificLayerInSQLite(layer.name()):
            return
        self.__connectSpecificSignals(layer)

    def __searchSpecificLayerInSQLite(self, layerName) -> bool:
        """
        Vérifie dans SQLite si un enregistrement dans la table des tables est présent pour le nom de la couche
        donnée en entrée.

        :param layerName: le nom de la couche à chercher
        :type layerName: str

        :return: True si l'enregistrement existe, False sinon
        """
        if SQLiteManager.selectColumnFromTableWithCondition("layer", cst.TABLEOFTABLES, "layer", layerName) \
                is not None:
            return True
        return False

    def __connectSpecificSignals(self, layer) -> None:
        """
        Connexion de deux signaux spécifiques :
         - QgsMalLayer.nameChanged, le nom de la couche a changé
         - QgsVectorLayer.beforeCommitChanges, juste avant d'envoyer les données vers le serveur

        :param layer: la couche modifiée
        :type layer: Optional[QgsMapLayer, QgsVectorLayer]
        """
        if layer is None:
            return
        layer.nameChanged.connect(self.__connectNameChanged)
        layer.beforeCommitChanges.connect(self.__connectBeforeCommitChanges)

    # TODO Mélanie remettre en service ?
    def __doSynchroWithTableOfTables(self) -> None:
        listLayersNotInTable = self.__isLayersInTableOfTables()
        if len(listLayersNotInTable) != 0:
            message = "Attention, la table générale SQLite est désynchronisée avec votre projet. Il faut extraire " \
                      "les couches suivantes :\n{0}".format(listLayersNotInTable)
            reply = QMessageBox.question(self.iface.mainWindow(), cst.IGNESPACECO, message, QMessageBox.Yes,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.__downloadLayersFromMyCommunity()

    # TODO Mélanie remettre en service ?
    def __isLayersInTableOfTables(self) -> list:
        layersNotInTable = []
        root = QgsProject.instance().layerTreeRoot()
        nodesGroup = root.findGroups()
        for ng in nodesGroup:
            if ng.name().find(cst.ESPACECO) == -1:
                continue
            qgsLayerTreelayers = ng.findLayers()
            for qgsLayerTreelayer in qgsLayerTreelayers:
                layer = qgsLayerTreelayer.layer()
                result = SQLiteManager.selectColumnFromTableWithCondition('layer', cst.TABLEOFTABLES, 'layer',
                                                                          layer.name())
                if result is None:
                    layersNotInTable.append(layer.name())
                    # message += "{0}\n".format(layer.name())
        return layersNotInTable
        # projectLayers = QgsProject.instance().mapLayers()
        # for k, v in projectLayers.items():
        #     if (v.name)
        #     result = SQLiteManager.selectColumnFromTableWithCondition('layer', cst.TABLEOFTABLES, 'layer', v.name())
        #     if result is None:
        #         message += "{0}\n".format(v.name())

    # TODO Mélanie remettre en service ?
    def __isObjectsAddedNotCommitted(self) -> dict:
        objNotCommitted = {}
        projectLayers = QgsProject.instance().mapLayers()
        for k, v in projectLayers.items():
            result = SQLiteManager.selectColumnFromTableWithCondition('idName', cst.TABLEOFTABLES, 'layer', v.name())
            if result is None:
                continue
            expr = "\"{0}\" == ''".format(result[0])
            it = v.getFeatures(QgsFeatureRequest().setFilterExpression(expr))
            for feature in it:
                objNotCommitted['added'] = (v, feature)
        return objNotCommitted

    def __connectNameChanged(self) -> None:
        """
        Connexion du signal layer.connectNameChanged pour interdire la modification du nom d'une couche
        qui a été extraite.
        """
        activeLayer = self.iface.activeLayer()
        if not self.__searchSpecificLayerInSQLite(activeLayer.name()):
            QMessageBox.warning(self.iface.mainWindow(), cst.IGNESPACECO,
                                "Action interdite ! Veuillez renommer la couche de son nom initial.")
        return

    def __connectBeforeCommitChanges(self) -> None:
        """
        Connexion du signal layer.beforeCommitChanges pour lancer la sauvegarde (requête POST) des données modifiées
        sur l'ensemble des couches en édition.
        """
        editLayers = []
        editableLayers = self.iface.editableLayers()
        for editableLayer in editableLayers:
            if not self.__searchSpecificLayerInSQLite(editableLayer.name()):
                continue
            if self.__isLayerEditBuffered(editableLayer) is True:
                editLayers.append(editableLayer)
        if len(editLayers) >= 1:
            if not self.__saveEdits(editLayers):
                return

    def __isLayerEditBuffered(self, layer) -> bool:
        """
        Vérifie si une couche a été modifiée : objets supprimés, modifiés ou ajoutés.

        :param layer: la couche qui a pu être mise à jour
        :type layer: QgsMapLayer

        :return: True, si la couche a été modifiée, False sinon
        """
        if layer is None:
            return False
        layerEditBuffer = layer.editBuffer()
        if layerEditBuffer is not None and (len(layerEditBuffer.allAddedOrEditedFeatures()) > 0
                                            or len(layerEditBuffer.deletedFeatureIds()) > 0):
            return True
        return False

    def __saveEdits(self, editableLayers) -> None:
        """
        Sauvegarde des mises à jour effectuées sur les couches quand l'utilisateur a cliqué sur la disquette (save)
        dans l'application QGIS.

        :param editableLayers: liste des couches modifiées
        :type editableLayers: list[QgsMapLayer]
        """
        allMessages = []
        for layer in editableLayers:
            messageProgress = "Synchronisation de la couche {}".format(layer.name())
            progress = ProgressBar(len(editableLayers), messageProgress)
            progress.setValue(1)
            allMessages.append(self.__saveChangesForOneLayer(layer))
            progress.close()
        # Message de fin de transaction
        dlgInfo = FormInfo()
        dlgInfo.textInfo.setText("<b>Contenu de la transaction</b>")
        dlgInfo.textInfo.setOpenExternalLinks(True)
        if len(allMessages) == 0:
            dlgInfo.textInfo.append("<br/>Vide")
        messageInfo = ''
        for messages in allMessages:
            messageInfo += messages
        dlgInfo.textInfo.append(messageInfo)
        dlgInfo.exec_()
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        if 'error' in messageInfo:
            return

    def __saveChangesForOneLayer(self, layer) -> str:
        """
        Sauvegarde des modifications d'UNE couche dans le projet QGIS par l'envoi d'une requête POST
        vers le serveur de l'espace collaboratif.

        :param layer: la couche qui doit être sauvegardée
        :type layer: QgsMapLayer

        :return: le message de fin de transaction avec le serveur
        """
        if layer is None:
            return "error : PluginModule:__saveChangesForOneLayer, la couche n'est pas valable (None)."
        # Connexion à l'Espace collaboratif
        # si res = 0, alors l'utilisateur à annuler son action
        if not self.__doConnexion(False):
            return "error : PluginModule:__saveChangesForOneLayer, pas de connexion, pas de transaction" \
                   " avec l'espace collaboratif."
        layersTableOfTables = SQLiteManager.selectColumnFromTable(cst.TABLEOFTABLES, 'layer')
        bRes = False
        if layersTableOfTables is not None:
            for layerTableOfTables in layersTableOfTables:
                if layer.name() in layerTableOfTables[0]:
                    bRes = True
                    break
        if not bRes:
            return "error : PluginModule:__saveChangesForOneLayer, la table {} n'existe pas " \
                   "dans la table des tables.".format(layer.name())
        editBuffer = layer.editBuffer()
        if not editBuffer:
            return "error : PluginModule:__saveChangesForOneLayer, pas de modifications trouvées" \
                   " pour la couche {}".format(layer.name())
        try:
            messages = self.__doPost(layer, editBuffer)
        except Exception as e:
            messages = '<br/><font color="red"><b>{0}</b> : {1}</font>'.format(layer.name(), e)
            QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
        return messages

    def __doConnexion(self, bAutomaticConnection) -> bool:
        """
        Connexion à l'espace collaboratif par l'authentification Keycloak.

        :param bAutomaticConnection: à True (connexion systématique), l'utilisateur a cliqué sur le bouton
                                     "Se connecter à l'Espace Collaboratif", False dans les autres cas.
        :type bAutomaticConnection: bool

        :return: True si la connexion a été établie, False sinon
        """
        if PluginHelper.getConfigFile() == '':
            PluginHelper.showMessageBox(cst.PROJECT_NOREGISTERED)
            return False

        if self.__context is None:
            self.__context = Contexte.getInstance(self, QgsProject)

        # si l'utilisateur crée un nouveau projet alors qu'il est déjà connecté sur son projet actuel, il faut
        # vérifier que les paramètres d'utilisation existent dans le projet
        self.__context.setProjectParams()

        # si l'utilisateur crée un nouveau projet alors qu'il est déjà connecté sur son projet actuel
        if QgsProject.instance().fileName().find(self.__context.projectFileName) == -1:
            return self.__context.getConnexionEspaceCollaboratifWithKeycloak(True)
        if bAutomaticConnection:
            return self.__context.getConnexionEspaceCollaboratifWithKeycloak(bAutomaticConnection)
        elif not bAutomaticConnection:
            if self.__context.getUserCommunity() is None:
                return self.__context.getConnexionEspaceCollaboratifWithKeycloak(True)
        return True

    def __doPost(self, layer, editBuffer) -> str:
        """
        Envoi par une requête POST, les mises à jour d'une couche vers le serveur de l'espace collaboratif.
        Ces mises à jour sont stockées par QGIS avec la classe QgsVectorLayerEditBuffer.

        :param layer: la couche mise à jour par l'utilisateur
        :type layer: QgsMapLayer

        :param editBuffer: les mises à jour stockées en mémoire pas QGIS
        :type editBuffer: QgsVectorLayerEditBuffer

        :return: message de fin de transaction
        """
        wfsPost = WfsPost(self.__context, layer, PluginHelper.load_CalqueFiltrage(self.__context.projectDir).text)
        # Juste avant la sauvegarde de QGIS, les modifications d'une couche sont envoyées au serveur,
        # le buffer est vidé, il ne faut pas laisser QGIS vider le buffer une deuxième fois sinon plantage
        bNormalWfsPost = False
        commitLayerResult = wfsPost.commitLayer(layer.name(), editBuffer, bNormalWfsPost)
        messages = "{0}\n".format(commitLayerResult['reporting'])
        if commitLayerResult['status'] == "FAILED":
            layer.destroyEditCommand()
        else:
            # Pour la couche synchronisée, il faut vider le buffer en mémoire en vérifiant que la fonction
            # commitLayer n'envoie pas d'exception sinon les modifs sont perdues
            # et l'outil redemande une synchronisation
            editBuffer.rollBack()
        return messages

    def __sendMessageBarException(self, message, exception) -> None:
        """
        Envoi d'un message d'erreur formaté avec l'exception à l'utilisateur sur la barre de message QGIS
        et dans le fichier de log.

        :param message: le message d'erreur
        :type message: str

        :param exception: le message d'exception
        :type exception: Exception
        """
        if self.__context is None:
            return
        self.__context.iface.messageBar().clearWidgets()
        self.__logger.error(format(exception))
        errorMessage = "{} : {}".format(message, str(exception))
        self.__context.iface.messageBar().pushMessage("Erreur", errorMessage, level=2, duration=5)
        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

    def __translate(self, message) -> str:
        """
        Fonction de traduction des noms de menus.
        """
        return QCoreApplication.translate('RipartPlugin', message)

    def __addAction(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True,
                    status_tip=None, whats_this=None, parent=None) -> QAction:
        """
        Add a toolbar icon to the toolbar
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self) -> None:
        """
        Create the menu entries and toolbar icons inside the QGIS GUI.
        """
        icon_path = ':/plugins/RipartPlugin/images/connect.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Se connecter a l\'Espace Collaboratif'),
            callback=self.__runConnexion,
            status_tip=self.__translate(u'Se connecter a l\'Espace Collaboratif'),
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/RipartPlugin/images/update.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Télécharger les signalements'),
            callback=self.__downloadReports,
            status_tip=self.__translate(u'Télécharger les signalements'),
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/RipartPlugin/images/viewRem.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Voir le signalement'),
            callback=self.__viewReport,
            status_tip=self.__translate(u'Voir le signalement'),
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/RipartPlugin/images/answer.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Répondre à un signalement'),
            callback=self.__replyToReport,
            status_tip=self.__translate(u'Répondre à un signalement'),
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/RipartPlugin/images/create.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Créer un nouveau signalement'),
            callback=self.__createReport,
            status_tip=self.__translate(u'Créer un nouveau signalement'),
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/RipartPlugin/images/cleaning.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Supprimer les signalements et les croquis associés de la carte en cours'),
            callback=self.__removeReportsAndSketchs,
            status_tip=self.__translate(u'Supprimer les signalements et les croquis associés de la carte en cours'),
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/RipartPlugin/images/magicwand.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Voir les objets associés'),
            callback=self.__magicwand,
            status_tip=self.__translate(u'Voir les objets associés'),
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/RipartPlugin/images/charger.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Charger les couches de ma communauté'),
            callback=self.__downloadLayersFromMyCommunity,
            status_tip=self.__translate(u'Charger les couches de ma communauté'),
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/RipartPlugin/images/synchroniser.png'
        self.__addAction(
            icon_path,
            text=self.__translate(u'Mettre à jour les couches Espace collaboratif'),
            callback=self.__synchronizeDataFromAllLayers,
            status_tip=self.__translate(u'Mettre à jour les couches Espace collaboratif'),
            parent=self.iface.mainWindow())

        # icon_path = ':/plugins/RipartPlugin/images/save.png'
        # self.__addAction(
        #     icon_path,
        #     text=self.__translate(u'Menu test'),
        #     callback=self.__test,
        #     status_tip=self.__translate(u'Menu test'),
        #     parent=self.iface.mainWindow())

        self.config.triggered.connect(self.__configurePlugin)
        self.config.setStatusTip(self.__translate(u"Ouvre la fenêtre de configuration du plugin."))
        self.about.triggered.connect(self.__ripAbout)
        self.help.triggered.connect(self.__showHelp)
        self.log.triggered.connect(self.__showLog)

        self.helpMenu = QMenu("Aide")
        self.helpMenu.addAction(self.config)
        self.helpMenu.addAction(self.help)
        self.helpMenu.addAction(self.log)
        self.helpMenu.addAction(self.about)
        self.toolButton2 = QToolButton()
        self.toolButton2.setMenu(self.helpMenu)
        self.toolButton2.setPopupMode(QToolButton.InstantPopup)
        self.toolButton2.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.toolButton2.setText("Aide")

        self.toolbar.addWidget(self.toolButton2)

    def __test(self):
        """
        Comme son nom l'indique, fonction de test pour des fonctionnalités QGIS.
        Désactivée pour l'instant.
        """
        layer = Contexte.getInstance(self, QgsProject).iface.activeLayer()
        for field in layer.fields():
            idx = layer.fields().indexOf(field.name())
            setup = layer.editorWidgetSetup(idx)
            widget_type = setup.type()
            config = setup.config()
            print(f"Champ : {field.name()}")
            print(f"  Type de widget : {widget_type}")
            print(f"  Configuration : {config}")
            # Résultats :
            # Champ : importance
            #     Type de widget : ValueMap
            #     Configuration : {'map': [{'': 'NULL'}, {'1': '1'}, {'2': '2'}, {'3': '3'}, {'4': '4'}, {'5': '5'},
            #                       {'6': '6'}]}
            #
            # Champ : fictif
            #     Type de widget : ValueMap
            #     Configuration : {'map': {'': 'NULL', 'Non': '0', 'Oui': '1'}}

        # fields = layer.fields()
        # for field in fields:
        #     name = field.name()
        #     if name != 'importance':
        #         continue
        #     index = fields.indexOf(name)
        #     ews = layer.editorWidgetSetup(index)
        #     print("Type: {}".format(ews.type()))
        #     # Résultat : Type: ValueMap
        #     print("Config: {}".format(ews.config()))
        #     # Résultat : Config: {'map': [{'': 'NULL'}, {'1': '1'}, {'2': '2'}, {'3': '3'}, {'4': '4'}, {'5': '5'},
        #     {'6': '6'}]}
        #     break

    def __runConnexion(self) -> None:
        """
        Connexion à l'Espace collaboratif.
        """
        try:
            if not self.__doConnexion(True):
                return
        except Exception as e:
            self.__sendMessageBarException('PluginModule.__runConnexion', e)

    def __downloadReports(self) -> None:
        """
        Téléchargement des signalements et croquis associés pour le groupe et la zone de travail de l'utilisateur.
        """
        try:
            # Connexion à l'Espace collaboratif
            if not self.__doConnexion(False):
                return
            # Téléchargement des signalements
            toolsReport = ToolsReport(self.__context)
            toolsReport.download()
        except Exception as e:
            self.__sendMessageBarException('PluginModule.__downloadReports', e)

    def __viewReport(self) -> None:
        """
        Visualisation des caractéristiques d'un signalement.
        """
        try:
            # Connexion à l'Espace collaboratif
            if not self.__doConnexion(False):
                return
            seeReport = SeeReport(self.__context)
            # TODO la réponse est bien envoyée mais vérifier pourquoi cela renvoie une exception ?
            self.__SeeReportView = seeReport.do()
        except Exception as e:
            self.__sendMessageBarException('PluginModule.__viewReport', e)

    def __replyToReport(self) -> None:
        """
        Envoyer une réponse à un signalement.
        """
        try:
            # Connexion à l'Espace collaboratif
            if not self.__doConnexion(False):
                return
            replyReport = ReplyReport(self.__context)
            replyReport.do()
        except Exception as e:
            self.__sendMessageBarException('PluginModule.__replyToReport', e)

    def __createReport(self) -> None:
        """
        Création d'un signalement géolocalisé avec ou sans croquis associé(s).
        """
        try:
            # Connexion à l'Espace collaboratif
            if not self.__doConnexion(False):
                return
            create = CreateReport(self.__context)
            create.do()

        except Exception as e:
            self.__sendMessageBarException('PluginModule.__createReport', e)

    def __removeReportsAndSketchs(self) -> None:
        """
        Suppression de tous les signalements et croquis de la carte courante du projet de l'utilisateur.
        """
        try:
            # Connexion à l'Espace collaboratif
            if not self.__doConnexion(False):
                return
            message = u"Êtes-vous sûr de vouloir supprimer les signalements et les croquis associés " \
                      u"de la carte en cours ?"
            reply = QMessageBox.question(self.iface.mainWindow(), cst.IGNESPACECO, message, QMessageBox.Yes,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                SQLiteManager.setEmptyTablesReportAndSketchs(PluginHelper.reportSketchLayersName)
                self.__context.refreshLayers()
            else:
                return
        except Exception as e:
            self.__sendMessageBarException('PluginModule.__removeReportsAndSketchs', e)

    def __magicwand(self) -> None:
        """
        Sélectionne le/les signalement(s) associé(s) au(x) croquis sélectionnés ou le/les croquis associé(s)
        au signalement sélectionné.
        On ne peut pas sélectionner des signalements et des croquis (soit signalements, soit croquis)
        """
        try:
            # Connexion à l'Espace collaboratif
            if not self.__doConnexion(False):
                return
            magicw = Magicwand(self.__context)
            magicw.selectReportOrSketchObjects()
        except Exception as e:
            self.__sendMessageBarException('PluginModule.__magicwand', e)

    def __downloadLayersFromMyCommunity(self) -> None:
        """
        Téléchargement des couches de travail en proposant un choix de couches téléchargeables appartenant
        au groupe de l'utilisateur.
        """
        try:
            # Connexion à l'Espace collaboratif
            if not self.__doConnexion(False):
                return
            # Les requêtes peuvent être longues
            messageProgress = "Groupe {} : récupération des couches".format(
                self.__context.getUserCommunity().getName())
            progress = ProgressBar(1, messageProgress)
            progress.setValue(1)
            # Il faut aller chercher les layers appartenant au groupe de l'utilisateur
            params = {'url': self.__context.urlHostEspaceCo, 'tokentype': self.__context.getTokenType(),
                      'tokenaccess': self.__context.getTokenAccess(), 'proxies': self.__context.proxies}
            community = Community(params)
            page = 1
            limit = 20
            listLayers = community.extractLayers(self.__context.getUserCommunity().getId(), page, limit)
            progress.close()
            if len(listLayers) == 0:
                raise Exception(u"Votre communauté n'a pas paramétré sa carte, il n'y a pas de données à charger.")
            # et les présenter à l'utilisateur pour qu'il fasse son choix de travail
            dlgChargerGuichet = FormChargerGuichet(self.__context, listLayers)
            # L'utilisateur a cliqué sur le bouton Annuler ou la croix du dialogue
            if dlgChargerGuichet.bRejected:
                return
            # Affichage de la boite
            dlgChargerGuichet.exec_()

        except Exception as e:
            self.__sendMessageBarException('PluginModule.__downloadLayersFromMyCommunity', e)

    def __synchronizeDataFromAllLayers(self) -> None:
        """
        Synchroniser les mises à jour de toutes les couches en édition/visualisation de la carte du projet utilisateur.
        """
        # TODO eric : réduire les lignes de code par des fonctions, code trop long
        try:
            endMessage = '<b>Contenu de la synchronisation</b>'

            # Connexion à l'Espace collaboratif
            if not self.__doConnexion(False):
                return

            # Il faut trouver parmi toutes les couches de la carte celles qui sont à synchroniser
            layersToSynchronize = []
            layersTableOfTables = SQLiteManager.selectColumnFromTable(cst.TABLEOFTABLES, 'layer')
            if layersTableOfTables is not None:
                for layer in QgsProject.instance().mapLayers().values():
                    for layerTableOfTables in layersTableOfTables:
                        if layer.name() == layerTableOfTables[0]:
                            print('synchronizeData couche : {}'.format(layer.name()))
                            layersToSynchronize.append(layer)
                            break

            # S'il n'y a pas de couches, la synchronisation est vide
            if len(layersToSynchronize) == 0:
                endMessage += "<br/>Vide\n"
            else:
                # Les couches à synchroniser contiennent-elles des données non enregistrées ?
                listEditBuffers = []
                messageLayers = ""
                for layer in layersToSynchronize:
                    layerEditBuffer = layer.editBuffer()
                    if layerEditBuffer is not None and (len(layerEditBuffer.allAddedOrEditedFeatures()) > 0
                                                        or len(layerEditBuffer.deletedFeatureIds()) > 0):
                        listEditBuffers.append(layerEditBuffer)
                        messageLayers += "{0}, ".format(layer.name())

                # Si oui envoi d'un message à l'utilisateur pour qu'il décide de la suite à donner
                if len(listEditBuffers) > 0:
                    if len(listEditBuffers) == 1:
                        startMessage = u"La couche {0} contient".format(messageLayers[0:len(messageLayers) - 2])
                    else:
                        startMessage = u"Les couches {0} contiennent".format(messageLayers[0:len(messageLayers) - 2])

                    message = "{0} des modifications non enregistrées. Si vous poursuivez la synchronisation, " \
                              "vos modifications seront perdues. \nVoulez-vous continuer ?".format(startMessage)
                    reply = QMessageBox.question(self.iface.mainWindow(), cst.IGNESPACECO, message, QMessageBox.Yes,
                                                 QMessageBox.No)
                    # On sort
                    if reply == QMessageBox.No:
                        return
                    else:
                        # On supprime les modifications et on poursuit
                        for editBuffer in listEditBuffers:
                            editBuffer.rollBack()

            # Synchronisation des couches une par une
            headers = {
                'Authorization': '{} {}'.format(self.__context.getTokenType(), self.__context.getTokenAccess())}
            spatialFilterName = PluginHelper.load_CalqueFiltrage(self.__context.projectDir).text
            progress = ProgressBar(len(QgsProject.instance().mapLayers()), cst.UPDATETEXTPROGRESS)
            i = 0
            for layer in layersToSynchronize:
                i += 1
                progress.setValue(i)
                endMessage += "<br/>{0}\n".format(layer.name())
                bbox = BBox(self.__context)
                parameters = {'layerName': layer.name(), 'bbox': bbox.getFromLayer(spatialFilterName, False, True),
                              'sridProject': cst.EPSGCRS4326, 'role': None,
                              'urlHostEspaceCo': self.__context.urlHostEspaceCo,
                              'headers': headers, 'proxies': self.__context.proxies}
                result = SQLiteManager.selectRowsInTableOfTables(layer.name())
                numrec = 0
                if len(result) > 0:
                    for r in result:
                        # r contient les items suivants :
                        # id/layer/idName/standard/database/databaseid/srid/geometryName/geometryDimension/geometryType/Numrec/tableid
                        # exemple :
                        # 8, 'Lignes', 'id_ligne', 1, 'test', 83, 2154, 'geom', 0, 'LineString', 0, 1531)
                        layer.idNameForDatabase = r[2]
                        parameters['isStandard'] = layer.isStandard = r[3]
                        parameters['databasename'] = layer.databasename = r[4]
                        parameters['databaseid'] = r[5]
                        parameters['sridLayer'] = r[6]
                        parameters['geometryName'] = r[7]
                        parameters['is3D'] = r[8]
                        layer.geometryTypeForDatabase = r[9]
                        parameters['numrec'] = numrec = r[10]
                        parameters['tableid'] = r[11]

                # la colonne detruit existe pour une table BDUni donc le booleen est mis à True par défaut
                bDetruit = True
                # si c'est une autre table donc standard alors la colonne n'existe pas
                # et il faut vider la table pour éviter de créer un objet à chaque Get
                if layer.isStandard:
                    bDetruit = False
                    SQLiteManager.emptyTable(layer.name())
                    SQLiteManager.vacuumDatabase()
                    layer.triggerRepaint()
                parameters['detruit'] = bDetruit
                # numrec = SQLiteManager.selectNumrecTableOfTables(layer.name())
                # parameters['numrec'] = numrec
                wfsGet = WfsGet(parameters)
                # Si le numrec stocké est le même que celui du serveur, alors il n'y a rien à synchroniser.
                # Il faut aussi qu'il soit égal à 1, ce numrec correspondant à une table non BDUni
                if not layer.isStandard:
                    maxNumrec = wfsGet.getMaxNumrec()
                    if numrec == maxNumrec:
                        endMessage += "<br/>Pas de mise à jour\n\n"
                        continue
                maxNumRecMessage = wfsGet.gcms_get()
                SQLiteManager.updateNumrecTableOfTables(layer.name(), maxNumRecMessage[0])
                SQLiteManager.vacuumDatabase()
                endMessage += "<br/>{0}\n".format(maxNumRecMessage[1])
            progress.close()

            # Message de fin de synchronisation
            dlgInfo = FormInfo()
            dlgInfo.textInfo.setText(endMessage)
            dlgInfo.exec_()
        except Exception as e:
            self.__sendMessageBarException('PluginModule.__synchronizeDataFromAllLayers', e)

    def __configurePlugin(self) -> None:
        """
        Lance la fenêtre de configuration des préférences de l'utilisateur.
        """
        try:
            self.__context = Contexte.getInstance(self, QgsProject)
            self.__context.checkConfigFile()
            self.__dlgConfigure = FormConfigure(context=self.__context)
            self.__dlgConfigure.exec_()
        except Exception as e:
            self.__sendMessageBarException('PluginModule.__configurePlugin', e)

    def __ripAbout(self) -> None:
        """
        Montre à l'utilisateur, la fenêtre (de classe FormInfo) avec les informations de version du plugin.
        """
        version = '0.'
        date = '2018'

        file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'metadata.txt'))

        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(file_path)
        if parser.has_section('general'):
            try:
                version = parser.get('general', 'version')
                date = parser.get('general', 'date')
            except Exception as e:
                self.__logger.error("No version/date in metadata : {}".format(e))

        dlgInfo = FormInfo()
        dlgInfo.textInfo.setText(u"<b>Plugin Espace Collaboratif</b>")
        dlgInfo.textInfo.append(
            u"<br/>Plugin intégrant les fonctionnalités de signalement et d'écriture de l'Espace collaboratif.")
        dlgInfo.textInfo.append(u"<br/>Version : " + version)
        dlgInfo.textInfo.append(u"\u00A9 IGN - " + date)
        dlgInfo.exec_()

    def __showHelp(self) -> None:
        """
        Ouvre le document d'aide utilisateur du plugin.
        """
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "files", PluginHelper.ripart_help_file))
        PluginHelper.open_file(file_path)

    def __showLog(self) -> None:
        """
        Ouvre le dernier fichier de log.
        """
        logpath = self.__ripartLogger.getLogpath()
        if logpath is not None:
            PluginHelper.open_file(logpath)

    def unload(self) -> None:
        """
        Fonction nécessaire au bon chargement du plugin
        """
        logs = logging.Logger.manager.loggerDict
        for lg in logs:
            logger = logs[lg]
            if isinstance(logger, logging.Logger):
                handlers = logger.handlers
                cntHandlers = len(logger.handlers)
                for i in range(cntHandlers - 1, -1, -1):
                    try:
                        if os.path.basename(handlers[i].name.baseFilename)[-10:] == u"plugin_espaceco.log":
                            handlers[i].close()
                            logger.removeHandler(handlers[i])
                    except AttributeError as e:
                        continue

        logdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')
        if os.path.exists(logdir):
            for f in os.listdir(logdir):
                file = open(os.path.join(logdir, f), 'r+')
                file.close()
                try:
                    os.remove(os.path.join(logdir, f))
                except Exception as e:
                    self.__logger.error(format(e))

        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.__translate(u'&IGN_Espace_Collaboratif'),
                action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar
