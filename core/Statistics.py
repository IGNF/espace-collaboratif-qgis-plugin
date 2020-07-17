from qgis.core import QgsVectorLayer

class Statistics(object):
    # Number total of features
    nft = None
    # Number of features added
    nfa = None
    # Number of features deleted
    nfd = None
    # Number of features changed
    nfc = None
    # list of id features added
    lFeaturesAdded = None
    # list of id features deleted
    lFeaturesDeleted = None
    # list of id features changed
    lFeaturesChanged = None

    # Layer to be count
    layer = None


    def __init__(self, layer):
        self.nft = layer.featureCount()
        self.nfa = 0
        self.nfd = 0
        self.nfc = 0
        self.layer = layer
        self.lFeaturesAdded = []
        self.lFeaturesDeleted = []


    def countFeaturesAdded(self):
        fid = None
        self.layer.featureAdded(fid)
        if fid != None:
            self.lFeaturesAdded.append(fid)


    def countFeaturesDeleted(self):
        fid = None
        self.layer.featureDeleted (fid)
        if fid != None:
            self.lFeaturesDeleted.append(fid)

        self.nfd = len(self.lFeaturesDeleted)


    def countFeaturesGeometryChanged(self):
        fid = None
        geom = None
        self.layer.geometryChanged(fid, geom)
        if fid != None:
            self.lFeaturesChanged.append(fid)

        self.nfc = len(self.lFeaturesChanged)


    def countFeaturesAttributeValueChanged(self):
        fid = None
        idx = None
        value = None
        self.layer.attributeValueChanged(fid, idx, value)
        if fid != None:
            self.lFeaturesChanged.append(fid)

        self.nfc = len(self.lFeaturesChanged)


    def run(self):
        print("Fin du comptage")
        #self.countFeaturesAdded()
        #self.countFeaturesDeleted()
        #self.countFeaturesGeometryChanged()
        #self.countFeaturesAttributeValueChanged()