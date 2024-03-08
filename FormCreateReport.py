# -*- coding: utf-8 -*-
"""
Created on 27 oct. 2015
Updated on 27 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""

import os

from PyQt5 import QtGui, QtWidgets, uic
from .core.RipartLoggerCl import RipartLogger

from PyQt5.QtCore import Qt, QDate, QDateTime, QTime
from PyQt5.QtWidgets import QTreeWidgetItem, QDialogButtonBox, QDateEdit, QDateTimeEdit

from .core.ClientHelper import ClientHelper
from .core import Constantes as cst
from .core.Theme import Theme
from .PluginHelper import PluginHelper
from .core.ThemeAttributes import ThemeAttributes

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormCreateReport_base.ui'))


class FormCreateReport(QtWidgets.QDialog, FORM_CLASS):
    """
    Formulaire pour la création d'une nouvelle remarque
    """
    logger = RipartLogger("FormCreateReport").getRipartLogger()

    bSend = False

    infogeogroups = []

    # le nom du fichier sélectionné (document joint)
    selFileName = None

    # dictionnaire des thèmes sélectionnés (key: nom du theme, value: l'objet Theme)
    selectedThemesList = {}

    # liste des thèmes préférés
    preferredThemes = []
    preferredGroup = ""

    # groupe sélectionné
    idSelectedGeogroup = ""

    # taille maximale du document joint
    docMaxSize = cst.MAX_TAILLE_UPLOAD_FILE

    def __init__(self, context, nbSketch, parent=None):
        """Constructor."""

        super(FormCreateReport, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.__context = context

        self.buttonBox.button(QDialogButtonBox.Ok).setText("Envoyer")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.onSend)

        self.checkBoxAttDoc.stateChanged.connect(self.openFileDialog)

        self.lblDoc.setProperty("visible", False)
        if nbSketch >= 2:
            self.radioBtnUnique.setChecked(False)
            self.radioBtnMultiple.setChecked(True)
            self.radioBtnMultiple.setText(u"Créer {0} signalements".format(nbSketch))

        self.__activeCommunity = self.__context.getActiveCommunityName()
        if self.__activeCommunity is None:
            profil = 'Profil par défaut'
        else:
            profil = self.__activeCommunity
        title = "{0} ({1})".format(self.__context.getUserNameCommunity(), profil)
        self.groupBoxProfil.setTitle(title)

        # les noms des thèmes préférés (du fichier de configuration)
        # TODO le theme prefere est-ils encore d'actualité ?
        # self.preferredThemes = PluginHelper.load_preferredThemes(self.__context.projectDir)
        preferredGroup = PluginHelper.load_preferredGroup(self.__context.projectDir)

        # Ajout des noms de groupes trouvés pour l'utilisateur
        self.__setComboBoxGroup()

        # Valeur par défaut : groupe actif
        bInListNameOfCommunities = False
        for nameid in self.__context.getListNameOfCommunities():
            if preferredGroup == nameid['name']:
                self.comboBoxGroupe.setCurrentText(preferredGroup)
                bInListNameOfCommunities = True
        if self.__activeCommunity is not None and self.__activeCommunity != "" and not bInListNameOfCommunities:
            self.comboBoxGroupe.setCurrentText(self.__activeCommunity)
        # TODO voir Noémie pour savoir si l'utilisateur peut être sans groupe
        # else:
            # self.__activeCommunity = 'Aucun'
            # self.comboBoxGroupe.setCurrentText('Aucun')

        # largeur des colonnes du treeview pour la liste des thèmes et de leurs attributs
        self.treeWidget.setColumnWidth(0, 160)
        self.treeWidget.setColumnWidth(1, 150)
        self.treeWidget.itemChanged.connect(self.__onItemChanged)

        # Affichage des thèmes du groupe de l'utilisateur
        self.__displayThemes(self.__context.getCommunity())

        # liste des thèmes du profil (objets Theme)
        __themesList = []

        # Modification des thèmes proposés en fonction du groupe sélectionné
        self.comboBoxGroupe.currentIndexChanged.connect(self.__groupIndexChanged)
        # self.groupIndexChanged(self.comboBoxGroupe.currentIndex())

        # TODO dans quel cas, on affiche tous les themes (je suppose de tous les groupes ?) profil aucun
        # self.profilThemesList = profil.allThemes

        self.docMaxSize = cst.MAX_TAILLE_UPLOAD_FILE
        # Pas de croquis à joindre, l'utilisateur a cliqué un point sur la carte
        if nbSketch == 0:
            self.checkBoxJoinCroquis.setChecked(False)

    def __setComboBoxGroup(self) -> None:
        for nameid in self.__context.getListNameOfCommunities():
            self.comboBoxGroupe.addItem(nameid['name'])
        if self.__activeCommunity is not None and self.__activeCommunity != "":
            self.comboBoxGroupe.setCurrentText(self.__activeCommunity)

    def __onItemChanged(self, item, column):
        if column != 0:
            return
        self.__toggle(item)
        state = item.checkState(column)
        if state == Qt.CheckState.Checked:
            self.treeWidget.expandItem(item)
        else:
            self.treeWidget.collapseItem(item)

    def __toggle(self, item):
        state = item.checkState(0)
        if state == Qt.CheckState.Unchecked:
            return
        numChildren = self.treeWidget.topLevelItemCount()
        for c in range(numChildren):
            tlItem = self.treeWidget.topLevelItem(c)
            if tlItem != item:
                tlItem.setCheckState(0, Qt.CheckState.Unchecked)

    def __displayThemesForCommunity(self, community):
        self.__themesList = community.getThemes()
        if len(self.__themesList) == 0:
            return
        for theme in self.__themesList:
            # Ajout du thème dans le treeview
            thItem = QTreeWidgetItem(self.treeWidget)
            thItem.setText(0, theme.getName())
            thItem.setText(1, '')
            self.treeWidget.addTopLevelItem(thItem)

            # Pour masquer la 2ème colonne TODO comprendre le pourquoi ???????
            thItem.setForeground(1, QtGui.QBrush(Qt.GlobalColor.white))

            # Il faut mettre une case à cocher devant chaque theme
            thItem.setCheckState(0, Qt.CheckState.Unchecked)

            # Affichage des attributs du thème et des modules d'aide à la saisie associés
            if len(theme.getAttributes()) == 0:
                continue
            for attribute in theme.getAttributes():
                attLabel = attribute.switchNameToTitle()
                label = QtWidgets.QLabel(attLabel, self.treeWidget)
                # Les attributs obligatoires sont en gras
                if attribute.getMandatory() is True:
                    myFont = QtGui.QFont()
                    myFont.setBold(True)
                    label.setFont(myFont)
                # Construction de l'attribut en fonction de son type
                item_value = self.__getItemValueFromType(attribute)
                attItem = QtWidgets.QTreeWidgetItem()
                thItem.addChild(attItem)
                self.treeWidget.setItemWidget(attItem, 0, label)
                self.treeWidget.setItemWidget(attItem, 1, item_value)

    def __displayThemes(self, community):
        """Affiche les thèmes dans le formulaire en fonction du groupe choisi.
        """
        for c in community.getCommunities():
            if self.__activeCommunity == c.getName():
                self.__displayThemesForCommunity(c)
                break

    '''
    Renvoie le type d'item pré-rempli avec sa valeur par défaut à afficher en face de chaque
    attribut du thème de signalement.
    '''
    def __getItemValueFromType(self, att):

        attType = att.getType()
        attDefaultval = att.getDefault()

        if attType == "checkbox":
            item_value = QtWidgets.QCheckBox(self.treeWidget)
            item_value.setChecked(False)
            if attDefaultval == '1' \
                    or attDefaultval == 'True' \
                    or attDefaultval == 'TRUE' \
                    or attDefaultval == 'true' \
                    or attDefaultval == 'Vrai' \
                    or attDefaultval == 'VRAI' \
                    or attDefaultval == 'vrai':
                item_value.setChecked(True)

        elif attType == 'date':
            item_value = QDateEdit()

            if attDefaultval is not None and attDefaultval != '':
                # '2020-10-28'
                date = attDefaultval.split('-')
                item_value.setDate(QDate(int(date[0]), int(date[1]), int(date[2])))

            item_value.setMinimumDate(QDate(1900, 1, 1))
            item_value.setMaximumDate(QDate(3000, 1, 1))
            item_value.setDisplayFormat("yyyy-MM-dd")

        elif attType == 'datetime':
            item_value = QDateTimeEdit()

            if attDefaultval is not None and attDefaultval != '':
                # '2020-08-15 12:23:48'
                dateTime = attDefaultval.split(' ')
                date = dateTime[0].split('-')
                time = dateTime[1].split(':')
                item_value.setDateTime(QDateTime(QDate(int(date[0]), int(date[1]), int(date[2])),
                                                 QTime(int(time[0]), int(time[1]), int(time[2]))))
            item_value.setMinimumDateTime(QDateTime(QDate(1900, 1, 1), QTime(0, 0, 0)))
            item_value.setMaximumDateTime(QDateTime(QDate(3000, 1, 1), QTime(0, 0, 0)))
            item_value.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        elif attType == 'list':
            valuesToDisplay = []
            attValues = att.getValues()
            if type(attValues) is dict:
                for c, v in attValues.items():
                    valuesToDisplay.append(c)
            elif type(attValues) is list:
                valuesToDisplay = attValues
            item_value = QtWidgets.QComboBox(self.treeWidget)
            item_value.insertItems(0, valuesToDisplay)

        else:
            item_value = QtWidgets.QLineEdit(self.treeWidget)
            item_value.setText(attDefaultval)

        return item_value

    def __groupIndexChanged(self):
        """Détecte le groupe choisi et lance l'affiche des thèmes adequats.
        """
        self.treeWidget.clear()
        print('__groupIndexChanged')
        userCommunityNameChoice = self.comboBoxGroupe.currentText()
        self.__activeCommunity = userCommunityNameChoice
        print(userCommunityNameChoice)
        if userCommunityNameChoice is not None:
            community = self.__context.getCommunity()
            for comm in community.getCommunities():
                print(comm.getName())
                if comm.getName() == userCommunityNameChoice:
                    print(comm.getThemes())
                    self.__displayThemesForCommunity(comm)
                    break

    def isSingleReport(self):
        """Indique si l'option de création d'une remarque unique a été choisie.
        """
        return self.radioBtnUnique.isChecked()

    def getMessage(self):
        """Retourne le message de la remarque
        """
        return self.textEditMessage.text()

    def getUserSelectedThemeWithAttributes(self):
        """Retourne la liste des thèmes (objets de type THEME) sélectionnés
        dans le formulaire de création du signalement
        """
        # Le signalement ne sera relié à aucun groupe
        communityId = -1
        for nameid in self.__context.getListNameOfCommunities():
            if self.__activeCommunity == nameid['name']:
                communityId = nameid['id']
                break
        data = {
            "community": communityId
        }
        root = self.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            thItem = root.child(i)

            if thItem.checkState(0) != Qt.CheckState.Checked:
                continue

            # Le nom du thème sélectionné
            data["theme"] = thItem.text(0)

            # Les attributs du theme remplis par l'utilisateur
            selectedAttributes = {}
            errorMessage = ''
            for j in range(thItem.childCount()):
                att = thItem.child(j)
                label = self.treeWidget.itemWidget(att, 0).text()
                key = self.__getKeyFromAttributeValue(label, thItem.text(0))
                widg = self.treeWidget.itemWidget(att, 1)
                val = self.__getValueFromWidget(widg, label, thItem.text(0))
                errorMessage += self.__correctValue(thItem.text(0), key, val)
                selectedAttributes[key] = val
                if errorMessage != '':
                    raise Exception(errorMessage)
            data["attributes"] = selectedAttributes
        return data

    def __correctValue(self, groupName, attributeName, value):
        errorMessage = ''
        for theme in self.__themesList:
            if theme.getName() != groupName:
                continue
            for attribute in theme.getAttributes():
                if attribute.getName() != attributeName:
                    continue
                if attribute.getType() == 'integer' or attribute.getType() == 'double':
                    if value != '' and not value.isdigit():
                        errorMessage = u"L'attribut {0} n'est pas valide.".format(attributeName)
                if attribute.getMandatory() is True:
                    if value == '' or value is None:
                        errorMessage = u"L'attribut {0} n'est pas valide.".format(attributeName)
        return errorMessage

    def __getValueFromWidget(self, widg, widg_label, theme_name):
        """
        Récupération au format adapté de la valeur saisie dans le formulaire pour chaque widget
        correspondant à un attribut du thème de signalement sélectionné.
        """

        if type(widg) == QtWidgets.QCheckBox:
            state = widg.checkState()
            if state == 0:
                val = "0"
            else:
                val = "1"

        elif type(widg) == QtWidgets.QLineEdit:
            val = widg.text()

        elif type(widg) == QtWidgets.QDateEdit:
            date = widg.date()
            val = date.toString('yyyy-MM-dd')

        elif type(widg) == QtWidgets.QDateTimeEdit:
            datetime = widg.dateTime()
            val = datetime.toString('yyyy-MM-dd hh:mm:ss')

        elif type(widg) == QtWidgets.QComboBox:
            form_value = widg.currentText()
            val = self.__getKeyFromListOfValues(form_value, widg_label, theme_name)

        else:
            val = widg.currentText()

        return val

    def __getKeyFromListOfValues(self, form_value, widg_label, theme_name):
        """Dans le cas d'une liste déroulante, on remplace si besoin la valeur récupérée dans la formulaire
         par la clé correspondante. Si la liste n'est en fait pas définie sous forme de <clés, valeurs>, la valeur
         récupérée dans le formulaire est directement utilisée.
        """

        # Récupération de l'objet Thème correspondant au nom du thème coché dans le formulaire
        th = self.__getThemeObject(theme_name)
        if th is None:
            return form_value

        # On parcourt les attributs du thème jusqu'à trouver celui qui correspond à widg_label
        found_att = False
        for att in th.getAttributes():
            if found_att:
                break

            if att.getTitle() != widg_label:
                continue

            # Une fois que l'attribut est trouvé, on remplace si besoin la valeur récupérée sur le formulaire par
            # la clé qui lui correspond dans la définition du thème
            found_att = True
            if type(att.getValues()) is dict:
                for c, v in att.getValues():
                    if v != "" and v == form_value:
                        val = c
                        return val

        return form_value

    def __getKeyFromAttributeValue(self, widg_label, theme_name):
        """Dans le cas d'une liste déroulante, on remplace si besoin la valeur récupérée dans la formulaire
         par la clé correspondante. Si la liste n'est en fait pas définie sous forme de <clés, valeurs>, la valeur
         récupérée dans le formulaire est directement utilisée.
        """

        # Récupération de l'objet Thème correspondant au nom du thème coché dans le formulaire
        th = self.__getThemeObject(theme_name)
        if th is None:
            return widg_label

        # On parcourt les attributs du thème jusqu'à trouver celui qui correspond à widg_label
        found_att = False
        for att in th.getAttributes():
            if found_att:
                break

            if att.getName() != widg_label:
                continue

            key = att.getName()
            return key

        return widg_label

    def __getThemeObject(self, themeName):
        """Retourne l'objet THEME à partir de son nom
        
        :param themeName: le nom du thème
        :type themeName: string
        
        :return l'objet Theme
        :rtype: Theme
        """
        for th in self.__themesList:
            if th.getName() == themeName:
                return th
        return None

    def countSelectedTheme(self):
        """Compte et retourne le nombre de thèmes sélectionnés
        
        :return le nombre de thèmes sélectionnés
        :rtype: int
        """
        return len(self.getSelectedThemes())

    def getAttachedDoc(self):
        """Retourne le nom du fichier sélectionné 
        
        :return nom du fichier sélectionné
        :rtype: string
        """
        if self.checkBoxAttDoc.isChecked():
            return self.selFileName
        else:
            return ""

    def optionWithAttDoc(self):
        """
        :rtype : boolean
        """
        return self.checkBoxAttDoc.isChecked()

    def optionWithCroquis(self):
        """
        :rtype : boolean
        """
        return self.checkBoxJoinCroquis.isChecked()

    def onSend(self):
        """Envoi de la requête de création au service ripart
        """
        # if self.textEditMessage.toPlainText().strip() == "":
        #     self.lblMessageError.setStyleSheet("QLabel { background-color : #F5A802; font-weight:bold}")
        #     self.lblMessageError.setText(u"Le message est obligatoire")
        #     self.__context.iface.messageBar().pushMessage("Attention", u'Le message est obligatoire', level=1,
        #                                                 duration=3)
        #     return
        self.bSend = True
        self.close()

    def truncate(self, n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

    def openFileDialog(self):
        if self.checkBoxAttDoc.isChecked():
            filters = u"All files (*.*);;" + \
                      u"Images (*.BMP;*.GIF;*.JPG;*.JPEG;*.PNG);;" + \
                      u"Tracées (*.GPX);;" + \
                      u"Textes (*.DOC;*.DOCX;*.ODT;*.PDF;*.TXT);;" + \
                      u"Tableurs (*.CSV;*.KML;*.ODS;*XLS;*.XLSX);;" + \
                      u"Compressés (*.ZIP;*.7Z)"

            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Document à joindre à la remarque', '.', filters)
            if filename != "":
                extension = os.path.splitext(filename)[1]
                sizeFilename = os.path.getsize(filename)
                if extension[1:] not in self.__context.formats:
                    message = u"Les fichiers de type '" + extension + u"' ne sont pas autorisés comme pièce-jointe " \
                                                                      u"pour l'Espace collaboratif. "
                    PluginHelper.showMessageBox(message)
                    self.checkBoxAttDoc.setCheckState(Qt.CheckState.Unchecked)

                elif sizeFilename > self.docMaxSize:
                    message = u"Le fichier \"" + filename + \
                              u"\" ne peut être envoyé à l'Espace collaboratif, car sa taille (" + \
                              str(os.path.getsize(filename) / 1000) + \
                              u" Ko) dépasse celle maximale autorisée (" + str(self.docMaxSize / 1000) + u" Ko)"

                    PluginHelper.showMessageBox(message)
                    self.checkBoxAttDoc.setCheckState(Qt.CheckState.Unchecked)

                else:
                    self.lblDoc.setProperty("visible", True)
                    fileNameWithSize = "{0} ({1}Mo)".format(filename, self.truncate(sizeFilename / (1024 * 1024), 3))
                    print(fileNameWithSize)
                    self.lblDoc.setText(fileNameWithSize)
                    self.selFileName = filename
            else:
                self.checkBoxAttDoc.setCheckState(Qt.CheckState.Unchecked)
                self.selFileName = None
        else:
            self.lblDoc.setProperty("visible", False)
            self.selFileName = None
