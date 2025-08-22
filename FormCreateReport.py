import json
import os

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QDate, QDateTime, QTime
from PyQt5.QtWidgets import QTreeWidgetItem, QDialogButtonBox, QDateEdit, QDateTimeEdit

from .core.PluginLogger import PluginLogger
from .core import Constantes as cst
from .core.Theme import Theme
from .core.CommunitiesMember import CommunitiesMember
from .core.Community import Community
from .core.ThemeAttributes import ThemeAttributes

from .PluginHelper import PluginHelper
from .Contexte import Contexte

from qgis.PyQt import QtCore

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'FormCreateReport_base.ui'))


class FormCreateReport(QtWidgets.QDialog, FORM_CLASS):
    """
    Classe du formulaire qui s'affiche dès la création d'un nouveau signalement.
    """
    logger = PluginLogger("FormCreateReport").getPluginLogger()

    bSend = False

    infogeogroups = []

    # la liste du (ou des) nom(s) du (ou des) fichiers sélectionnés (document(s) joint(s))
    __selFilesName = []

    # dictionnaire des thèmes sélectionnés (key : nom du theme, value: l'objet Theme)
    selectedThemesList = {}

    # liste des thèmes préférés
    preferredThemes = []
    preferredGroup = ""

    # groupe sélectionné
    idSelectedGeogroup = ""

    # taille maximale du document joint
    docMaxSize = cst.MAX_TAILLE_UPLOAD_FILE

    __communityIdWhenThemeChanged = None

    def __init__(self, context, nbSketch, parent=None) -> None:
        """
        Constructor.

        :param context: le contexte du projet et ses cartes
        :type context: Contexte

        :param nbSketch: le nombre de croquis à joindre lors de la création d'un signalement, à 0 si pas de croquis dans
                         le cas d'une création d'un signalement avec un clic sur la carte
        :type nbSketch: int
        """
        super(FormCreateReport, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.__context = context

        self.buttonBox.button(QDialogButtonBox.Ok).setText("Envoyer")
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.__onSend)

        self.checkBoxAttDoc.stateChanged.connect(self.__openFileDialog)

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

        # La liste des fichiers joints au signalement
        self.__files = {}
        # les données liées au signalement à envoyer au serveur
        self.__datas = {}

    def __setComboBoxGroup(self) -> None:
        """
        Initialisation de la liste déroulante en ajoutant tous les groupes de l'utilisateur. Le groupe actif de
        l'utilisateur est placé en tête de liste.
        """
        for nameid in self.__context.getListNameOfCommunities():
            self.comboBoxGroupe.addItem(nameid['name'])
        if self.__activeCommunity is not None and self.__activeCommunity != "":
            self.comboBoxGroupe.setCurrentText(self.__activeCommunity)

    def __onItemChanged(self, item, column) -> None:
        """
        Ouverture/fermeture des attributs hiérarchisés dès que l'utilisateur clique sur la case à cocher du thème.

        :param item: le thème sous forme de case à cocher
        :type item: QTreeWidgetItem

        :param column: les attributs du thème hiérarchisés sous forme de colonne
        :type column: int
        """
        if column != 0:
            return
        self.__toggle(item)
        state = item.checkState(column)
        if state == Qt.CheckState.Checked:
            self.treeWidget.expandItem(item)
        else:
            self.treeWidget.collapseItem(item)

    def __toggle(self, item) -> None:
        """
        Sélection unique d’un thème dans l'arborescence Thème/Attributs en s'assurant qu’un seul élément "thème"
        soit coché à la fois.

        :param item: le thème sous forme de case à cocher
        :type item: QTreeWidgetItem
        """
        state = item.checkState(0)
        if state == Qt.CheckState.Unchecked:
            return
        numChildren = self.treeWidget.topLevelItemCount()
        for c in range(numChildren):
            tlItem = self.treeWidget.topLevelItem(c)
            if tlItem != item:
                tlItem.setCheckState(0, Qt.CheckState.Unchecked)

    def __removeRedIfValid(self, widg, label, theme_name):
        key = self.__getKeyFromAttributeValue(label, theme_name)
        val = self.__getValueFromWidget(widg, label, theme_name)
        errorMessage = self.__correctValue(theme_name, key, val)
        if errorMessage == '':
            widg.setStyleSheet("")

    def __displayThemesForCommunity(self, community) -> None:
        """
        Initialisation de l'arborescence pour les thèmes/attributs.

        :param community: groupe utilisateur avec ses informations (les thèmes liés au groupe par exemple)
        :type community: Community
        """
        self.__themesList = community.getTheme()
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
                attLabel = attribute.switchNameToAlias()
                label = QtWidgets.QLabel(attLabel, self.treeWidget)
                # Les attributs obligatoires sont en gras
                if attribute.getMandatory() is True:
                    myFont = QtGui.QFont()
                    myFont.setBold(True)
                    label.setFont(myFont)
                # Construction de l'attribut en fonction de son type
                item_value = self.__getQtWidgetsFromTypeAttribute(attribute)
                attItem = QtWidgets.QTreeWidgetItem()
                thItem.addChild(attItem)
                self.treeWidget.setItemWidget(attItem, 0, label)
                self.treeWidget.setItemWidget(attItem, 1, item_value)
                # L'utilisateur a tendance à travailler sur les attributs et oublie de cocher le thème.
                # Avec l'ajout d'une connexion pour tous les types de "widgets attributs", le thème est coché
                # automatiquement.
                # Le signal stateChanged est appelé à chaque coche/décoche
                if isinstance(item_value, QtWidgets.QCheckBox):
                    item_value.stateChanged.connect(
                        lambda state, parent_item=thItem, widg=item_value, lab=attLabel, theme_name=thItem.text(0): (
                            self.__checkParentOnCheckBoxChanged(parent_item, state),
                            self.__removeRedIfValid(widg, lab, theme_name)))
                # Le signal currentIndexChanged est appelé à chaque changement de sélection
                elif isinstance(item_value, QtWidgets.QComboBox):
                    item_value.currentIndexChanged.connect(
                        lambda idx, parent_item=thItem, combo=item_value, widg=item_value, lab=attLabel,
                        theme_name=thItem.text(0): (
                            self.__checkParentOnComboChanged(parent_item, combo),
                            self.__removeRedIfValid(widg, lab, theme_name)))
                # Le signal textChanged est appelé à chaque modification du texte
                elif isinstance(item_value, QtWidgets.QLineEdit):
                    item_value.textChanged.connect(
                        lambda text, parent_item=thItem, lineedit=item_value, widg=item_value, lab=attLabel,
                        theme_name=thItem.text(0): (
                            self.__checkParentOnLineEditChanged(parent_item, lineedit),
                            self.__removeRedIfValid(widg, lab, theme_name)))
                # Le signal dateChanged est appelé à chaque modification de date
                elif isinstance(item_value, QDateEdit):
                    item_value.dateChanged.connect(
                        lambda date, parent_item=thItem, dateedit=item_value, widg=item_value, lab=attLabel,
                        theme_name=thItem.text(0): (
                            self.__checkParentOnDateEditChanged(parent_item, dateedit),
                            self.__removeRedIfValid(widg, lab, theme_name)))
                # Le signal dateTimeChanged est appelé à chaque modification de dateTime
                elif isinstance(item_value, QDateTimeEdit):
                    item_value.dateTimeChanged.connect(
                        lambda datetime, parent_item=thItem, datetimeedit=item_value, widg=item_value, lab=attLabel,
                        theme_name=thItem.text(0): (
                            self.__checkParentOnDateTimeEditChanged(parent_item, datetimeedit),
                            self.__removeRedIfValid(widg, lab, theme_name)))

    def __displayThemes(self, community) -> None:
        """
        Affiche les thèmes et leurs attributs sous forme d'arborescence dans le formulaire en fonction
        du groupe choisi par l'utilisateur.

        :param community: liste des groupes (avec leurs caractéristiques) de l'utilisateur
        :type community: CommunitiesMember
        """
        for c in community.getCommunities():
            if self.__activeCommunity == c.getName():
                self.__displayThemesForCommunity(c)
                break

    def __getQtWidgetsFromTypeAttribute(self, att) -> QtWidgets:
        """
        Choisi en fonction du type d'attribut, le QtWidgets correspondant et le rempli avec la valeur
        par défaut de l'attribut.

        :param att:
        :type att: ThemeAttributes

        :return: le type de QtWidgets ((QLineEdit, QComboBox, QCheckBox, QDateEdit, QDateTimeEdit)
        """
        attType = att.getType()
        attDefaultval = att.getDefault()

        if attType == 'checkbox':
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

    def __checkParentOnCheckBoxChanged(self, parent_item, state) -> None:
        """
        Fonction pour cocher/décocher automatiquement la case de la colonne "thème" (case mère) lorsque l’utilisateur
        coche la QCheckBox dans la colonne "attribut" (case fille). Signal "stateChanged".
        NB : quand une case fille est décochée, vérifie si toutes les cases filles sont décochées, et si oui,
        décoche la case mère.

        :param parent_item: case mère, QCheckBox du thème
        :type parent_item: QTreeWidgetItem

        :param state: état de la QCheckBox (case mère), cochée/non cochée
        :type state: bool
        """
        if state == Qt.CheckState.Checked:
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        else:
            # Vérifier si toutes les cases filles sont décochées
            all_unchecked = True
            for i in range(parent_item.childCount()):
                child_item = parent_item.child(i)
                widget = self.treeWidget.itemWidget(child_item, 1)
                if isinstance(widget, QtWidgets.QCheckBox) and widget.isChecked():
                    all_unchecked = False
                    break

            if all_unchecked:
                parent_item.setCheckState(0, Qt.CheckState.Unchecked)

    def __checkParentOnComboChanged(self, parent_item, combo) -> None:
        """
        Fonction pour cocher/décocher automatiquement la case de la colonne "thème" (case mère) lorsque l’utilisateur
        change la valeur de la QComboBox dans la colonne "attribut" (case fille). Signal "currentIndexChanged"
        NB : si tous les attributs enfants sont vides/non sélectionnés, le thème parent est décoché.

        :param parent_item: case mère, QcheckBox du thème
        :type parent_item: QTreeWidgetItem

        :param combo: zone de liste déroulante
        :type combo: QComboBox
        """
        if combo.currentText().strip() != "":
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        else:
            self.__checkAllChildrenEmpty(parent_item)

    def __checkParentOnLineEditChanged(self, parent_item, lineedit) -> None:
        """
        Fonction pour cocher/décocher automatiquement la case de la colonne "thème" (case mère) lorsque l’utilisateur
        change la valeur de la QLineEdit dans la colonne "attribut" (case fille). Signal "textChanged"
        NB : si tous les attributs enfants sont vides/non sélectionnés, le thème parent est décoché.

        :param parent_item: case mère, QcheckBox du thème
        :type parent_item: QTreeWidgetItem

        :param lineedit: la zone de texte
        :type lineedit: QLineEdit
        """
        if lineedit.text().strip() != "":
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        else:
            # Si toutes les cases filles sont décochées, décoche la case mère
            self.__checkAllChildrenEmpty(parent_item)

    def __checkParentOnDateEditChanged(self, parent_item, dateedit) -> None:
        """
        Fonction pour cocher/décocher automatiquement la case de la colonne "thème" (case mère) lorsque l’utilisateur
        change la valeur de la QDateEdit dans la colonne "attribut" (case fille). Signal "dateChanged"
        NB : si tous les attributs enfants sont vides/non sélectionnés, le thème parent est décoché.

        :param parent_item: case mère, QcheckBox du thème
        :type parent_item: QTreeWidgetItem

        :param dateedit: la zone de texte de la date
        :type dateedit: QDateEdit
        """
        min_date = QDate(1900, 1, 1)
        if dateedit.date() != min_date:
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        else:
            # Si toutes les cases filles sont décochées, décoche la case mère
            self.__checkAllChildrenEmpty(parent_item)

    def __checkParentOnDateTimeEditChanged(self, parent_item, datetimeedit) -> None:
        """
        Fonction pour cocher/décocher automatiquement la case de la colonne "thème" (case mère) lorsque l’utilisateur
        change la valeur de la QDateTimeEdit dans la colonne "attribut" (case fille). Signal "dateTimeChanged"
        NB : si tous les attributs enfants sont vides/non sélectionnés, le thème parent est décoché.

        :param parent_item: case mère, QcheckBox du thème
        :type parent_item: QTreeWidgetItem

        :param datetimeedit: la zone de texte de la dateTime
        :type datetimeedit: QDateTimeEdit
        """
        min_datetime = QDateTime(QDate(1900, 1, 1), QTime(0, 0, 0))
        if datetimeedit.dateTime() != min_datetime:
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        else:
            # Si toutes les cases filles sont décochées, décoche la case mère
            self.__checkAllChildrenEmpty(parent_item)

    def __checkAllChildrenEmpty(self, parent_item) -> None:
        """
        Fonction utilitaire pour décocher le parent (case à cocher thème) si tous les attributs
        sont vides/non sélectionnés.

        :param parent_item: case mère, QcheckBox du thème
        :type parent_item: QTreeWidgetItem
        """
        all_empty = True
        for i in range(parent_item.childCount()):
            child_item = parent_item.child(i)
            widget = self.treeWidget.itemWidget(child_item, 1)
            if isinstance(widget, QtWidgets.QCheckBox):
                if widget.isChecked():
                    all_empty = False
                    break
            elif isinstance(widget, QtWidgets.QComboBox):
                if widget.currentText().strip() != "":
                    all_empty = False
                    break
            elif isinstance(widget, QtWidgets.QLineEdit):
                if widget.text().strip() != "":
                    all_empty = False
                    break
            elif isinstance(widget, QDateEdit):
                if widget.date() != QDate(1900, 1, 1):
                    all_empty = False
                    break
            elif isinstance(widget, QDateTimeEdit):
                if widget.dateTime() != QDateTime(QDate(1900, 1, 1), QTime(0, 0, 0)):
                    all_empty = False
                    break
        if all_empty:
            parent_item.setCheckState(0, Qt.CheckState.Unchecked)

    def getCommunityIdWhenThemeChanged(self):
        """

        """
        return self.__communityIdWhenThemeChanged

    def __groupIndexChanged(self):
        """
        Détecte le groupe choisi et lance l'affiche des thèmes adéquats.
        """
        self.treeWidget.clear()
        userCommunityNameChoice = self.comboBoxGroupe.currentText()
        self.__activeCommunity = userCommunityNameChoice
        if userCommunityNameChoice is not None:
            community = self.__context.getCommunity()
            for comm in community.getCommunities():
                if comm.getName() == userCommunityNameChoice:
                    self.__displayThemesForCommunity(comm)
                    self.__communityIdWhenThemeChanged = comm.getId()
                    break

    def isSingleReport(self):
        """
        Indique si l'option de création d'une remarque unique a été choisie.
        """
        return self.radioBtnUnique.isChecked()

    def getComment(self):
        """
        :return: le texte entré par l'utilisateur (partie Commentaire)
        """
        return self.textEditMessage.toPlainText()

    def getUserSelectedThemeWithAttributes(self) -> []:
        """
        Retourne la liste des thèmes (objets de type THEME) sélectionnés
        dans le formulaire de création du signalement.
        :return: la liste de la liste des erreurs de validation par attribut.
        """
        # errors = list of tuples: (error_message, widget)
        errors = []
        root = self.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            thItem = root.child(i)

            if thItem.checkState(0) != Qt.CheckState.Checked:
                continue

            # Le nom du thème
            themeName = thItem.text(0)
            bFind = False
            for theme in self.__themesList:
                if theme.getName() == themeName:
                    self.__datas['community'] = theme.getCommunityId()
                    bFind = True
                    break
            if not bFind:
                self.__datas['community'] = -1
            self.__datas['theme'] = themeName
            # Les attributs du theme remplis par l'utilisateur
            selectedAttributes = {}
            for j in range(thItem.childCount()):
                att = thItem.child(j)
                label = self.treeWidget.itemWidget(att, 0).text()
                key = self.__getKeyFromAttributeValue(label, thItem.text(0))
                widg = self.treeWidget.itemWidget(att, 1)
                val = self.__getValueFromWidget(widg, label, thItem.text(0))
                errorMessage = self.__correctValue(thItem.text(0), key, val)
                if errorMessage != '':
                    errors.append((errorMessage, widg))
                valueChangedIfTypeAttributeIsJson = self.__getJsonValue(thItem.text(0), key, val)
                selectedAttributes[key] = str(valueChangedIfTypeAttributeIsJson)
            if len(errors) == 0:
                self.__datas['attributes'] = selectedAttributes
        return errors

    def __correctValue(self, groupName, attributeName, value) -> str:
        # TODO corriger le message par le nom affiché et non par le nom interne exemple
        # L'attribut website n'est pas valide par L'attribut Site web n'est pas valide
        # TODO il faut envoyer une liste de messages et non un par un
        """
        :return: le message d'erreur pour l'attribut passé en entrée
        """
        error = ''
        for theme in self.__themesList:
            if theme.getName() != groupName:
                continue
            for attribute in theme.getAttributes():
                bError = False
                if attribute.getName() != attributeName:
                    continue
                if attribute.getType() == 'integer':
                    if value != '' and not value.isdigit():
                        bError = True
                if attribute.getType() == 'double' or attribute.getType() == 'float':
                    if value != '':
                        tmp = value.replace('.', '')
                        if not tmp.isdigit():
                            bError = True
                if attribute.getMandatory() is True:
                    if value == '' or value is None or value == '0':
                        bError = True
                if bError:
                    error = "L'attribut {0} n'est pas valide.".format(attribute.switchNameToAlias())
                # Si le break est atteint l'attribut a été contrôlé, inutile de continuer
                break
            break
        return error

    def __getJsonValue(self, groupName, attributeName, value):
        valueChangedIfTypeAttributeIsJson = value
        for theme in self.__themesList:
            if theme.getName() != groupName:
                continue
            for attribute in theme.getAttributes():
                if attribute.getName() != attributeName:
                    continue
                if attribute.getType() != 'jsonvalue':
                    continue
                valueChangedIfTypeAttributeIsJson = json.loads(value)
        return valueChangedIfTypeAttributeIsJson

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
        """Dans le cas d'une liste déroulante, on remplace si besoin la valeur récupérée dans le formulaire
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

            if att.switchNameToAlias() != widg_label:
                continue

            # Une fois que l'attribut est trouvé, on remplace si besoin la valeur récupérée sur le formulaire par
            # la clé qui lui correspond dans la définition du thème
            found_att = True
            values = att.getValues()
            if type(values) is dict:
                for c, v in values.items():
                    if c != "" and c == form_value:
                        val = v
                        return val

        return form_value

    def __getKeyFromAttributeValue(self, widg_label, theme_name):
        """Dans le cas d'une liste déroulante, on remplace si besoin la valeur récupérée dans le formulaire
         par la clé correspondante. Si la liste n'est en fait pas définie sous forme de <clés, valeurs>, la valeur
         récupérée dans le formulaire est directement utilisée.
        """

        # Récupération de l'objet Thème correspondant au nom du thème coché dans le formulaire
        th = self.__getThemeObject(theme_name)
        if th is None:
            return widg_label

        # On parcourt les attributs du thème jusqu'à trouver celui qui correspond à widg_label
        for att in th.getAttributes():
            if att.switchNameToAlias() != widg_label:
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

    def getFilesAttachments(self) -> {}:
        """
        Retourne une (ou plusieurs) chaine(s) binaire(s)
        
        :return: la liste des fichiers transformés en string($binary)
        """
        if self.checkBoxAttDoc.isChecked():
            return self.__files
        else:
            return {}

    def getDatasForRequest(self):
        return self.__datas

    # Envoi de la requête de création à l'espace collaboratif
    def __onSend(self):
        # Il faut au moins un theme coché
        nb = 0
        root = self.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            thItem = root.child(i)
            if thItem.checkState(0) == Qt.CheckState.Checked:
                nb = 1
        # Pas de thème sélectionné
        if nb == 0:
            self.lblMessageError.setText("Attention, il manque la sélection du thème.")
            self.bSend = False
            return
        # Commentaire de 10 caractères minimum
        if len(self.textEditMessage.toPlainText()) < 10:
            self.lblMessageError.setText("Attention, le commentaire doit être de 10 caractères minimum.")
            self.bSend = False
            return

        # Nouvelle logique : récupération des données et des erreurs
        try:
            errors = self.getUserSelectedThemeWithAttributes()
        except Exception as e:
            # Gestion d'erreur imprévue
            self.lblMessageError.setText(f"Erreur interne: {str(e)}")
            self.bSend = False
            return

        # Retire le rouge de tous les widgets avant nouvelle validation
        root = self.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            thItem = root.child(i)
            for j in range(thItem.childCount()):
                att = thItem.child(j)
                widg = self.treeWidget.itemWidget(att, 1)
                if widg:
                    widg.setStyleSheet("")

        if errors:
            messages = ''
            for msg, widg in errors:
                if widg:
                    # Colore en rouge les widgets invalides
                    widg.setStyleSheet("border: 2px solid red;")
                messages += "{}\n".format(msg)
            # Affiche les erreurs dans lblMessageError séparées par des retours à la ligne
            self.lblMessageError.setText(messages)
            self.bSend = False
            return

        # Si pas d'erreur, on ferme le dialogue
        self.bSend = True
        self.close()

    def __truncate(self, n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

    def __openFileDialog(self):
        self.__files.clear()
        if not self.checkBoxAttDoc.isChecked():
            self.checkBoxAttDoc.setCheckState(Qt.CheckState.Unchecked)
            self.lblDoc.setProperty("visible", False)
            self.__selFilesName.clear()
        else:
            filters = u"All files (*.*);;" + \
                      u"Images (*.BMP;*.GIF;*.JPG;*.JPEG;*.PNG);;" + \
                      u"Tracées (*.GPX);;" + \
                      u"Textes (*.DOC;*.DOCX;*.ODT;*.PDF;*.TXT);;" + \
                      u"Tableurs (*.CSV;*.KML;*.ODS;*XLS;*.XLSX);;" + \
                      u"Compressés (*.ZIP;*.7Z)"
            filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'Document à joindre à la remarque', '.',
                                                                  filters)
            if len(filenames) == 0:
                self.checkBoxAttDoc.setCheckState(Qt.CheckState.Unchecked)
            message = ''
            if len(filenames) > 4:
                message += "Maximum 4 fichiers liés à un signalement\n"
                PluginHelper.showMessageBox(message)
                self.checkBoxAttDoc.setCheckState(Qt.CheckState.Unchecked)
            elif 0 < len(filenames) < 5:
                for filename in filenames:
                    extension = os.path.splitext(filename)[1]
                    if extension[1:] not in self.__context.formats:
                        if extension not in message:
                            message += "Les fichiers de type '{}' ne sont pas autorisés comme pièce-jointe pour " \
                                       "l'Espace collaboratif.\n".format(extension)
                    sizeFilename = os.path.getsize(filename)
                    if sizeFilename > self.docMaxSize:
                        message += u"Le fichier {0} ne peut être envoyé à l'Espace collaboratif, car sa taille " \
                                   u"({1}Ko) dépasse celle maximale autorisée ({2}Ko).\n" \
                            .format(filename, str(sizeFilename / 1000), str(self.docMaxSize / 1000))
                if message != '':
                    PluginHelper.showMessageBox(message)
                    self.checkBoxAttDoc.setCheckState(Qt.CheckState.Unchecked)
                else:
                    # Affichage des documents sélectionnés dans l'espace dédié
                    self.lblDoc.setProperty("visible", True)
                    fileNameWithSize = ''
                    for filename in filenames:
                        # La liste des fichiers pour affichage dans la boite
                        sizeFilename = os.path.getsize(filename)
                        fileNameWithSize += "{0} ({1}Mo)\n".format(
                            filename, self.__truncate(sizeFilename / (1024 * 1024), 3))
                        self.__selFilesName.append(filename)
                        # Les fichiers à uploader sous forme de dictionnaire
                        # Exemple : files = {'save.png': open('D:/Temp/save.png', 'rb')}
                        names = filename.split('/')
                        # self.__files.update({names[len(names) - 1]: open(filename, 'rb')}) # fonctionne à garder
                        # exemple requests_toolbelt : 'field2': ('filename', open('file.py', 'rb'), 'text/plain')
                        # self.__files.update({names[len(names) - 1]: (names[len(names) - 1], open(filename, 'rb'))})
                        # {'file': ('example.txt', open('example.txt', 'rb'), 'multipart/form-data')}
                        self.__files.update({names[len(names) - 1]: (names[len(names) - 1], open(filename, 'rb'),
                                                                     'multipart/form-data')})
                        # Traduction dans la requête
                        # {'save.png': <_io.BufferedReader name='D:/Temp/save.png'>}
                    self.lblDoc.setText(fileNameWithSize)
