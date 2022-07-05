# -*- coding: utf-8 -*-
"""
Created on 27 oct. 2015
Updated on 27 nov. 2020

version 4.0.1, 15/12/2020

@author: AChang-Wailing, EPeyrouse, NGremeaux
"""

import os

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from .core.RipartLoggerCl import RipartLogger

from PyQt5.QtCore import Qt, QDate, QDateTime, QTime, pyqtSlot
from PyQt5.QtWidgets import QTreeWidgetItem, QDialogButtonBox, QDateEdit, QDateTimeEdit

from .core.ClientHelper import ClientHelper
from .core import ConstanteRipart as cst
from .core.Theme import Theme
from .RipartHelper import RipartHelper
from .core.ThemeAttribut import ThemeAttribut

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormCreerRemarque_base.ui'))


class FormCreerRemarque(QtWidgets.QDialog, FORM_CLASS):
    """
    Formulaire pour la création d'une nouvelle remarque
    """
    logger = RipartLogger("FormCreerRemarque").getRipartLogger()
    context = None

    bSend = False

    infogeogroups = []

    # le nom du fichier sélectionné (document joint)
    selFileName = None

    # dictionnaire des thèmes sélectionnés (key: nom du theme, value: l'objet Theme)
    selectedThemesList = {}

    # liste des thèmes du profil (objets Theme)
    profilThemesList = []

    # liste des thèmes préférés
    preferredThemes = []
    preferredGroup = ""

    # groupe sélectionné
    idSelectedGeogroup = ""

    # taille maximale du document joint
    docMaxSize = cst.MAX_TAILLE_UPLOAD_FILE

    def __init__(self, context, NbSketch, parent=None):
        """Constructor."""

        super(FormCreerRemarque, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.context = context

        self.buttonBox.button(QDialogButtonBox.Ok).setText("Envoyer")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.onSend)

        self.checkBoxAttDoc.stateChanged.connect(self.openFileDialog)

        self.lblDoc.setProperty("visible", False)
        if NbSketch >= 2:
            self.radioBtnUnique.setChecked(False)
            self.radioBtnMultiple.setChecked(True)
            self.radioBtnMultiple.setText(u"Créer {0} signalements".format(NbSketch))

        profil = self.context.client.getProfil()

        if profil.geogroup.name is not None:
            self.groupBoxProfil.setTitle(profil.author.name + " (" + profil.geogroup.name + ")")
        else:
            self.groupBoxProfil.setTitle(profil.author.name + u" (Profil par défaut)")

        # les noms des thèmes préférés (du fichier de configuration)
        self.preferredThemes = RipartHelper.load_preferredThemes(self.context.projectDir)
        preferredGroup = RipartHelper.load_preferredGroup(self.context.projectDir)

        # Ajout des noms de groupes trouvés pour l'utilisateur
        self.infosgeogroups = profil.infosGeogroups
        listeNamesGroups = []
        for igg in self.infosgeogroups:
            self.comboBoxGroupe.addItem(igg.group.name)
            listeNamesGroups.append(igg.group.name)

        # Valeur par défaut : groupe actif
        groupeActif = self.context.groupeactif
        if preferredGroup in listeNamesGroups:
            self.comboBoxGroupe.setCurrentText(preferredGroup)
        else:
            if groupeActif is not None and groupeActif != "" and groupeActif in listeNamesGroups:
                self.comboBoxGroupe.setCurrentText(groupeActif)
            else:
                groupeActif = 'Aucun'
                self.comboBoxGroupe.setCurrentText('Aucun')

        # largeur des colonnes du treeview pour la liste des thèmes et de leurs attributs
        self.treeWidget.setColumnWidth(0, 160)
        self.treeWidget.setColumnWidth(1, 150)
        self.treeWidget.itemChanged.connect(self.onItemChanged)

        # On modifie les thèmes proposés en fonction du groupe sélectionné
        if groupeActif != 'Aucun':
            self.comboBoxGroupe.currentIndexChanged.connect(self.groupIndexChanged)
            self.groupIndexChanged(self.comboBoxGroupe.currentIndex())
        else:
            self.displayThemes(profil.globalThemes, profil.themes)

        self.profilThemesList = profil.allThemes

        self.docMaxSize = self.context.client.get_MAX_TAILLE_UPLOAD_FILE()

    def onItemChanged(self, item, column):
        if column != 0:
            return
        self.toggle(item)
        state = item.checkState(column)
        if state == Qt.Checked:
            self.treeWidget.expandItem(item)
        else:
            self.treeWidget.collapseItem(item)

    def toggle(self, item):
        state = item.checkState(0)
        if state == Qt.Unchecked:
            return
        numChildren = self.treeWidget.topLevelItemCount()
        for c in range(numChildren):
            tlItem = self.treeWidget.topLevelItem(c)
            if tlItem != item:
                tlItem.setCheckState(0, Qt.Unchecked)

    def displayThemes(self, filteredThemes, themes):
        """Affiche les thèmes dans le formulaire en fonction du groupe choisi.
        """
        global th
        preferredThemes = self.preferredThemes

        if len(themes) <= 0:
            return

        # boucle sur tous les thèmes filtrés du groupe
        for thName in filteredThemes:

            # On cherche l'objet theme correspondant dans la liste des themes
            foundTheme = False
            for th in themes:
                if th.group.name == thName:
                    foundTheme = True
                    break

            if not foundTheme:
                continue

            # Si le thème n'est pas dans le filtre du profil, on ne l'affiche pas
            if not th.isFiltered:
                continue

            # ajout du thème dans le treeview
            thItem = QTreeWidgetItem(self.treeWidget)
            thItem.setText(0, th.group.name)
            thItem.setText(1, th.group.id)
            self.treeWidget.addTopLevelItem(thItem)

            # Pour masquer la 2ème colonne (qui contient le groupe id)
            thItem.setForeground(1, QtGui.QBrush(Qt.white))

            if ClientHelper.notNoneValue(th.group.name) in preferredThemes:
                thItem.setCheckState(0, Qt.Checked)
                thItem.setExpanded(True)
            else:
                thItem.setCheckState(0, Qt.Unchecked)

            # Affichage des attributs du thème et des modules d'aide à la saisie associés
            for att in th.attributes:
                attLabel = att.tagDisplay
                attType = att.type
                attDefaultval = att.defaultval

                label = QtWidgets.QLabel(attLabel, self.treeWidget)
                # Les attributs obligatoires sont en gras
                if att.obligatoire is True:
                    myFont = QtGui.QFont()
                    myFont.setBold(True)
                    label.setFont(myFont)

                item_value = self.get_item_value_from_type(att)

                attItem = QtWidgets.QTreeWidgetItem()
                thItem.addChild(attItem)
                self.treeWidget.setItemWidget(attItem, 0, label)
                self.treeWidget.setItemWidget(attItem, 1, item_value)

    '''
    Renvoie le type d'item pré-rempli avec sa valeur par défaut à afficher en face de chaque
    attribut du thème de signalement.
    '''

    def get_item_value_from_type(self, att):

        item_value = ""

        attType = att.type
        attDefaultval = att.defaultval

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
            valeursToDisplay = []
            for c, v in att.valeurs.items():
                if v == "":
                    valeursToDisplay.append(c)
                else:
                    valeursToDisplay.append(v)
            item_value = QtWidgets.QComboBox(self.treeWidget)
            item_value.insertItems(0, valeursToDisplay)

        else:
            item_value = QtWidgets.QLineEdit(self.treeWidget)
            item_value.setText(attDefaultval)

        return item_value

    def groupIndexChanged(self, index):
        """Détecte le groupe choisi et lance l'affiche des thèmes adequats.
        """
        self.treeWidget.clear()

        infosgeogroup = self.infosgeogroups[index]
        nameGroup = infosgeogroup.group.name
        self.idSelectedGeogroup = infosgeogroup.group.id

        # Affichage du commentaire par défaut dans la fenêtre message
        georemComment = infosgeogroup.georemComment
        if georemComment != "":
            self.textEditMessage.setText(georemComment)
        if nameGroup == self.context.groupeactif:
            themes = self.context.profil.themes
            filteredThemes = self.context.profil.filteredThemes
        else:
            themes = infosgeogroup.themes
            filteredThemes = infosgeogroup.filteredThemes

        self.preferredGroup = nameGroup

        self.displayThemes(filteredThemes, themes)

    def isSingleRemark(self):
        """Indique si l'option de création d'une remarque unique a été choisie.
        """
        return self.radioBtnUnique.isChecked()

    def getMessage(self):
        """Retourne le message de la remarque
        """
        return self.textEditMessage.text()

    def getSelectedThemes(self):
        """Retourne la liste des thèmes (objets de type THEME) sélectionnés
        dans le formulaire de création du signalement
        """
        selectedThemes = []

        root = self.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            thItem = root.child(i)

            if thItem.checkState(0) != Qt.Checked:
                continue

            theme = Theme()
            theme.group.name = thItem.text(0)
            theme.group.id = thItem.text(1)

            for j in range(thItem.childCount()):
                att = thItem.child(j)
                label = self.treeWidget.itemWidget(att, 0).text()
                key = self.get_key_from_attribute_value(label, thItem.text(0))
                widg = self.treeWidget.itemWidget(att, 1)

                val = self.get_value_from_widget(widg, label, theme.group.name)

                attribut = ThemeAttribut(theme.group.name, ClientHelper.notNoneValue(key),
                                         ClientHelper.notNoneValue(val))
                theme.attributes.append(attribut)

            selectedThemes.append(theme)

        return selectedThemes

    def get_value_from_widget(self, widg, widg_label, theme_name):
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
            val = self.get_key_from_list_of_values(form_value, widg_label, theme_name)

        else:
            val = widg.currentText()

        return val

    def get_key_from_list_of_values(self, form_value, widg_label, theme_name):
        """Dans le cas d'une liste déroulante, on remplace si besoin la valeur récupérée dans la formulaire
         par la clé correspondante. Si la liste n'est en fait pas définie sous forme de <clés, valeurs>, la valeur
         récupérée dans le formulaire est directement utilisée.
        """

        # Récupération de l'objet Thème correspondant au nom du thème coché dans le formulaire
        th = self._getThemeObject(theme_name)
        if th is None:
            return form_value

        # On parcourt les attributs du thème jusqu'à trouver celui qui correspond à widg_label
        found_att = False
        for att in th.attributes:
            if found_att:
                break

            if att.tagDisplay != widg_label:
                continue

            # Une fois que l'attribut est trouvé, on remplace si besoin la valeur récupérée sur le formulaire par
            # la clé qui lui correspond dans la définition du thème
            found_att = True
            for c, v in att.valeurs.items():
                if v != "" and v == form_value:
                    val = c
                    return val

        return form_value

    def get_key_from_attribute_value(self, widg_label, theme_name):
        """Dans le cas d'une liste déroulante, on remplace si besoin la valeur récupérée dans la formulaire
         par la clé correspondante. Si la liste n'est en fait pas définie sous forme de <clés, valeurs>, la valeur
         récupérée dans le formulaire est directement utilisée.
        """

        # Récupération de l'objet Thème correspondant au nom du thème coché dans le formulaire
        th = self._getThemeObject(theme_name)
        if th is None:
            return widg_label

        # On parcourt les attributs du thème jusqu'à trouver celui qui correspond à widg_label
        found_att = False
        for att in th.attributes:
            if found_att:
                break

            if att.tagDisplay != widg_label:
                continue

            key = att.nom
            return key

        return widg_label

    def _getThemeObject(self, themeName):
        """Retourne l'objet THEME à partir de son nom
        
        :param themeName: le nom du thème
        :type themeName: string
        
        :return l'objet Theme
        :rtype: Theme
        """
        for th in self.profilThemesList:
            if th.group.name == themeName:
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
        if self.textEditMessage.toPlainText().strip() == "":
            self.lblMessageError.setStyleSheet("QLabel { background-color : #F5A802; font-weight:bold}")
            self.lblMessageError.setText(u"Le message est obligatoire")
            self.context.iface.messageBar().pushMessage("Attention", u'Le message est obligatoire', level=1,
                                                        duration=10)
            return

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
                if extension[1:] not in self.context.formats:
                    message = u"Les fichiers de type '" + extension + u"' ne sont pas autorisés comme pièce-jointe " \
                                                                      u"pour l'Espace collaboratif. "
                    RipartHelper.showMessageBox(message)
                    self.checkBoxAttDoc.setCheckState(Qt.Unchecked)

                elif sizeFilename > self.docMaxSize:
                    message = u"Le fichier \"" + filename + \
                              u"\" ne peut être envoyé à l'Espace collaboratif, car sa taille (" + \
                              str(os.path.getsize(filename) / 1000) + \
                              u" Ko) dépasse celle maximale autorisée (" + str(self.docMaxSize / 1000) + u" Ko)"

                    RipartHelper.showMessageBox(message)
                    self.checkBoxAttDoc.setCheckState(Qt.Unchecked)

                else:
                    self.lblDoc.setProperty("visible", True)
                    fileNameWithSize = "{0} ({1}Mo)".format(filename, self.truncate(sizeFilename / (1024 * 1024), 3))
                    print(fileNameWithSize)
                    self.lblDoc.setText(fileNameWithSize)
                    self.selFileName = filename
            else:
                self.checkBoxAttDoc.setCheckState(Qt.Unchecked)
                self.selFileName = None
        else:
            self.lblDoc.setProperty("visible", False)
            self.selFileName = None
