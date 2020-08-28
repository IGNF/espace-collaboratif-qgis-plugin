from PyQt5.QtCore import QVariant
from qgis.core import QgsVectorLayer, QgsProject, QgsEditorWidgetSetup
from.Statistics import Statistics
import hashlib
import os

class GuichetVectorLayer(QgsVectorLayer):

    # Les statistiques de comptage pour la couche
    stat = None

    # La liste des id/md5 par objet AVANT le travail de l'utilisateur
    md5BeforeWorks = []

    # La liste des id/md5 par objet APRES le travail de l'utilisateur
    md5AfterWorks = []

    # Les fichiers ou sont stockés les objets
    repertoire = None
    fileBeforeWorks = None
    fileAfterWorks = None


    def getStat(self):
        return self.stat


    def openFile(self, nameFile, mode):
        file = open(nameFile, mode)
        return file


    def closeFile(self, fileToClose):
        fileToClose.close()


    '''
    Connection des signaux
    Initialisation des comptages
    '''
    def init(self, projectDirectory, layerName):
        self.connectSignals()
        self.stat = Statistics(self.featureCount())
        self.repertoire = projectDirectory
        fileName = QgsProject.instance().fileName()
        tmp = fileName.replace(".qgz", "")
        nodeGroups = QgsProject.instance().layerTreeRoot().findGroups()
        self.fileAfterWorks = "{}{}{}_{}".format(tmp, nodeGroups[0].name(), layerName, "md5AfterWorks.txt")
        self.fileBeforeWorks = "{}{}{}_{}".format(tmp, nodeGroups[0].name(), layerName, "md5BeforeWorks.txt")


    '''
    Connection des signaux pour les évènements survenus sur la carte
    '''
    def connectSignals(self):
        #self.geometryChanged.connect(self.geometry_changed)
        #self.attributeValueChanged.connect(self.attribute_value_changed)
        #self.featureAdded.connect(self.feature_added)
        #self.featuresDeleted.connect(self.features_deleted)
        self.attributeAdded.connect(self.attribute_added)
        self.attributeDeleted.connect(self.attribute_deleted)
        self.editingStopped.connect(self.editing_stopped)


    '''
    Calcul d'une clé de hachage à partir des caractéristiques d'un objet
    # géométrie et valeurs de ses attributs
    '''
    def setMD5(self, feature):
        allAttributes = []

        # Ajout de la géometrie
        allAttributes.append("{}".format(feature.geometry().asJson()))

        # Ajout de la liste des valeurs d'attributs
        listValues = feature.attributes()
        for value in listValues:
            allAttributes.append("{}".format(value))

        # Concaténation et encodage des valeurs d'attributs
        tmp = "".join(allAttributes).encode('utf-8')

        # Calcul de la clé
        cle = hashlib.sha224(tmp).hexdigest()
        print("{}:{}".format(feature.id(),cle))

        # Retourne la référence par objet (idQGIS:MD5)
        return (feature.id(), cle)


    '''
    Au chargement de la couche dans QGIS, les caractéristiques des objets initiaux
    sont stockées dans un fichier sous la forme d'une clé de hachage :
    id QGIS/clé de hachage
    '''
    def setMd5BeforeWorks(self):
        # il faut détruire le fichier afterWorks
        if os.path.exists(self.fileAfterWorks):
            os.remove(self.fileAfterWorks)

        fichier = self.openFile(self.fileBeforeWorks, "wt")
        features = self.getFeatures()
        for feature in features:
            id_cle = self.setMD5(feature)
            self.md5BeforeWorks.append(id_cle)
            fichier.write("{}:{}{}".format(id_cle[0], id_cle[1], "\n"))
        self.closeFile(fichier)


    '''
    Dès la fin de l'édition d'une couche, les caractéristiques des objets
    sont stockées dans un fichier sous la forme d'une clé de hachage :
    id QGIS/clé de hachage
    Il doit y avoir des objets créés, modifiés, supprimés
    '''
    def setMd5AfterWorks(self):
        fichier = self.openFile(self.fileAfterWorks, "wt")
        features = self.getFeatures()
        for feature in features:
            id_cle = self.setMD5(feature)
            self.md5AfterWorks.append(id_cle)
            fichier.write("{}:{}{}".format(id_cle[0], id_cle[1], "\n"))
        self.closeFile(fichier)


    '''
    L'utilisateur a mis fin à l'édition de la couche,
    les objets sont stockés dans un fichier
    '''
    def editing_stopped(self):
        self.setMd5AfterWorks()



    # Je pense qu'il faut interdire cette action ?
    def attribute_deleted(self, idx):
        print("Action impossible, voir Noémie")
        return


    # Je pense qu'il faut interdire cette action ?
    def attribute_added(self, idx):
        print("Action impossible, voir Noémie")
        return


    '''
    Comptage par différentiel des objets
    ajoutés, supprimés ou modifiés de la couche
    '''
    def doDifferentielAfterBeforeWorks(self):
        # Ajout
        self.stat.nfa = 0
        # Suppression
        self.stat.nfd = 0
        # Modification
        self.stat.nfc = 0

        # Dictionnaire cle/valeur carte origine
        before = self.openFile(self.fileBeforeWorks, "r")
        lines = before.readlines()
        dictBefore = {}
        for line in lines:
            tmp = line.split(":")
            dictBefore[tmp[0]] = tmp[1]
        self.closeFile(before)

        # oublie de sauvegarder le projet : pas de fichier after
        if not os.path.exists(self.fileAfterWorks):
            return

        # Dictionnaire cle/valeur carte après intervention utilisateur
        after = self.openFile(self.fileAfterWorks, "r")
        lines = after.readlines()
        dictAfter = {}
        for line in lines:
            tmp = line.split(":")
            dictAfter[tmp[0]] = tmp[1]
        self.closeFile(after)

        '''
        Différentiel entre les deux dictionnaires
        '''
        # Ajout/modification d'éléments
        for cle, md5 in dictAfter.items():
            if cle not in dictBefore:
                print ("feature {} ajouté".format(cle))
                self.stat.nfa += 1
            else:
               if md5 != dictBefore[cle]:
                   print ("feature {} : modifié".format(cle))
                   self.stat.nfc += 1

        # Suppression d'éléments
        for cle, md5 in dictBefore.items():
            if cle not in dictAfter:
                print ("feature {} : supprimé".format(cle))
                self.stat.nfd += 1


    '''
    Liste des champs de la couche
    '''
    def getFields(self):
        fields = self.fields()
        for field in fields:
            name = field.name()
            if name != 'zone':
                continue

            index = fields.indexOf(name)
            type = 'ValueMap'
            config = {'map': [{'Zone1': 'Zone1'},{' Zone2': ' Zone2'}, {'Zone3': 'Zone3'}]}
            setup = QgsEditorWidgetSetup(type, config)
            self.setEditorWidgetSetup(index, setup)





    # Les objets détruits sont comptés et stockés dans une liste
    '''def features_deleted(self, fids):
        for fid in fids:
            print('Features {} deleted'.format(fid))
            self.stat.lFeaturesDeleted.append(fid)
        self.stat.nfd = len(self.stat.lFeaturesDeleted)


    # Les objets ajoutés sont comptés et stockés dans une liste
    def feature_added(self, fid):
        print('Feature {} added'.format(fid))
        self.stat.lFeaturesAdded.append(fid)
        self.stat.nfa = len(self.stat.lFeaturesAdded)


    # Les objets dont la valeur d'un attribut a changé
    # sont comptés et stockés dans une liste
    def attribute_value_changed(self, fid, idx, value):
        print('Attribute value of feature {} changed'.format(fid))
        self.stat.lFeaturesChanged.append(fid)
        self.stat.nfc = len(self.stat.lFeaturesChanged)


    # Les objets dont la géométrie a changé
    # sont comptés et stockés dans une liste
    def geometry_changed(self, fid, geometry):
        print('Geometry of feature {} changed'.format(fid))
        self.stat.lFeaturesChanged.append(fid)
        self.stat.nfc = len(self.stat.lFeaturesChanged)'''