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
    #lFeaturesAdded = None
    # list of id features deleted
    #lFeaturesDeleted = None
    # list of id features changed
    #lFeaturesChanged = None


    def __init__(self, nbObjectsInLayer):
        self.nft = nbObjectsInLayer
        self.nfa = 0
        self.nfd = 0
        self.nfc = 0
        #self.lFeaturesAdded = []
        #self.lFeaturesDeleted = []
        #self.lFeaturesChanged = []


    def count(self):
        print("Objets au total : {}".format(self.nft + self.nfa - self.nfd))
        print("Objets ajoutés : {}".format(self.nfa))
        print("Objets détruits : {}".format(self.nfd))
        print("Objets modifiés : {}".format(self.nfc))


    def countToDialog(self, layerName):
        message = ""
        message += "{} objets au total\n".format(self.nft + self.nfa - self.nfd)
        message += "{} objets créés\n".format(self.nfa)
        message += "{} objets modifiés\n".format(self.nfc)
        message += "{} objets supprimés\n\n".format(self.nfd)
        return message