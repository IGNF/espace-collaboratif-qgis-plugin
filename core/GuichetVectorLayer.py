from qgis.core import QgsVectorLayer
from.Statistics import Statistics
import hashlib

class GuichetVectorLayer(QgsVectorLayer):

    # Les statistiques de comptage pour la couche
    stat = None

    # La liste des id/md5 par objet avant le travail de l'utilisateur
    md5BeforeWorks = []

    # La liste des id/md5 par objet après le travail de l'utilisateur
    md5AfterWorks = []

    repertoire = None
    fileAfterWorks = None
    fileBeforeWorks = None


    def getStat(self):
        return self.stat


    def openFile(self, nameFile, mode):
        file = open(nameFile, mode)
        return file


    def closeFile(self, fileToClose):
        fileToClose.close()


    # Connection des signaux
    # Initialisation des comptages
    def init(self, projectDirectory):
        self.connectSignals()
        self.stat = Statistics(self.featureCount())
        self.repertoire = projectDirectory
        self.fileAfterWorks = "{}/{}".format(self.repertoire, "md5AfterWorks.txt")
        self.fileBeforeWorks = "{}/{}".format(self.repertoire, "md5BeforeWorks.txt")



    # Connection des signaux pour les évènements survenus sur la carte
    def connectSignals(self):
        #self.geometryChanged.connect(self.geometry_changed)
        #self.attributeValueChanged.connect(self.attribute_value_changed)
        #self.featureAdded.connect(self.feature_added)
        #self.featuresDeleted.connect(self.features_deleted)
        self.attributeAdded.connect(self.attribute_added)
        self.attributeDeleted.connect(self.attribute_deleted)
        self.afterRollBack.connect(self.after_rollback)
        self.editingStopped.connect(self.editing_stopped)


    # Calcul d'une clé de hachage à partir des caractéristiques d'un objet
    # géométrie et valeurs de ses attributs
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

        # Retourne la référence par objet (id:MD5)
        return (feature.id(), cle)


    # Calcul d'une clé de hachage pour les objets initiaux
    # au chargement de la couche dans QGIS
    def setMD5md5BeforeWorks(self):
        fichier = self.openFile(self.fileBeforeWorks, "wt")
        features = self.getFeatures()
        for feature in features:
            id_cle = self.setMD5(feature)
            self.md5BeforeWorks.append(id_cle)
            fichier.write("{}:{}{}".format(id_cle[0], id_cle[1], "\n"))
        self.closeFile(fichier)


    # L'utilisateur a mis fin à l'édition de la couche
    def editing_stopped(self):
        self.setMD5md5AfterWorks()


    # L'utilisateur a annulé ses modifs
    def after_rollback(self):
        print("L'utilisateur a annulé son travail")
        # Il y a quelque chose à faire


    # Calcul d'une clé de hachage pour les objets créés, modifiés, supprimés
    def setMD5md5AfterWorks(self):
        fichier = self.openFile(self.fileAfterWorks, "wt")
        features = self.getFeatures()
        for feature in features:
            id_cle = self.setMD5(feature)
            self.md5AfterWorks.append(id_cle)
            fichier.write("{}:{}{}".format(id_cle[0], id_cle[1], "\n"))
        self.closeFile(fichier)


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


    # Je pense qu'il faut interdire cette action ?
    def attribute_deleted(self, idx):
        print("Action impossible, voir Noémie")
        return


    # Je pense qu'il faut interdire cette action ?
    def attribute_added(self, idx):
        print("Action impossible, voir Noémie")
        return


    # Comptage des actions sur la carte : ajouts, suppressions, modifications
    def doDifferentielAfterBeforeWorks(self):
        self.stat.nfa = 0
        self.stat.nfd = 0
        self.stat.nfc = 0
        before = self.openFile(self.fileBeforeWorks, "r")
        lines = before.readlines()
        dictBefore = {}
        for line in lines:
            tmp = line.split(":")
            dictBefore[tmp[0]] = tmp[1]
        self.closeFile(before)

        after = self.openFile(self.fileAfterWorks, "r")
        lines = after.readlines()
        dictAfter = {}
        for line in lines:
            tmp = line.split(":")
            dictAfter[tmp[0]] = tmp[1]
        self.closeFile(after)

        # Ajout/modification d'éléments
        for cle, md5 in dictAfter.items():
            if cle not in dictBefore:
                print ("{} : ajout".format(cle))
                self.stat.nfa += 1
            else:
               if md5 != dictBefore[cle]:
                   print("{} : modification".format(cle))
                   self.stat.nfc += 1

        # Suppression d'éléments
        for cle, md5 in dictBefore.items():
            if cle not in dictAfter:
                print ("{} : suppression".format(cle))
                self.stat.nfd += 1
