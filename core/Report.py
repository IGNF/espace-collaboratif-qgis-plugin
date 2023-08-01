class Report(object):

    def __init__(self, data):
        self.__noSignalement = data['id']
        self.__auteur = data['author']
        self.__commune = data['commune']['title']
        self.__insee = data['commune']['name']
        self.__departement = data['departement']['title']
        self.__departementId = data['departement']['name']
        self.__dateCreation = data['opening_date']
        self.__dateMaj = data['updating_date']
        self.__dateValidation = data['closing_date']
        self.__themes = ''
        self.__statut = data['status']
        self.__message = data['comment']
        self.__reponses = ''
        self.__url = ''
        self.__urlPrive = ''
        self.__document = ''
        self.__autorisation = ''
        self.__geom = data['geometry']
        # Nouvelles variables
        # self.__replies = data['replies']
        # self.__attachments = data['attachments']
        # self.__community = data['community']
        # self.__author = data['author']
        # self.__validator = data['validator']
        # self.__id = data['id']
        # self.__commune = data['commune']
        # self.__departement = data['departement']
        # self.__territory = data['territory']
        # self.__geometry = data['geometry']
        # self.__comment = data['comment']
        # self.__opening_date = data['opening_date']
        # self.__closing_date = data['closing_date']
        # self.__updating_date = data['updating_date']
        # self.__attributes = data['attributes']
        # self.__status = data['status']
        # self.__sketch_xml = data['sketch_xml']
        # self.__sketch = data['sketch']
        # self.__input_device = data['input_device']
        # self.__device_version = data['device_version']
