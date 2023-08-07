class Report(object):

    def __init__(self, urlHostEspaceCo, data) -> None:
        self.__urlHostEspaceCo = urlHostEspaceCo
        self.__id = data['id']
        self.__author = data['author']
        self.__commune = data['commune']['title']
        self.__insee = data['commune']['name']
        self.__departement = data['departement']['title']
        self.__departementId = data['departement']['name']
        self.__dateCreation = data['opening_date']
        self.__dateMaj = data['updating_date']
        self.__dateValidation = data['closing_date']
        self.__themes = self.getStrThemes(data['attributes'])
        self.__statut = data['status']
        self.__message = data['comment']
        self.__replies = self.getStrReplies(data['replies'])
        self.__url = self.setUrl(data['id'])
        self.__urlPrive = ''
        self.__attachments = self.getStrAttachments(data['attachments'])
        self.__autorisation = ''
        self.__comment = data['comment']
        self.__inputDevice = data['input_device']
        self.__geometry = data['geometry']
        # TODO autres variables retournées par l'API, que fait-on ?
        # self.__community = data['community']
        # self.__validator = data['validator']
        # self.__territory = data['territory']
        # self.__attributes = data['attributes']
        # self.__sketch_xml = data['sketch_xml']
        # self.__sketch = data['sketch']
        # self.__input_device = data['input_device']

    def getId(self) -> int:
        return self.__id

    def getComment(self) -> str:
        return self.__comment

    def getAttachments(self) -> str:
        return self.__attachments

    def getThemes(self) -> str:
        return self.__themes

    def getReplies(self) -> str:
        return self.__replies

    def getAuthor(self) -> str:
        return self.__author

    def getCommune(self) -> str:
        return self.__commune

    def getInsee(self) -> str:
        return self.__insee

    def getDateCreation(self) -> str:
        return self.__dateCreation

    def getStatut(self) -> str:
        return self.__statut

    def getInputDevice(self) -> str:
        return self.__inputDevice

    def getGeometry(self) -> str:
        return self.__geometry

    #  Concatène les réponses existantes d'un signalement
    def concatenateReplies(self) -> str:
        concatenate = ""

        if len(self.__replies) == 0:
            concatenate += "Ce signalement n'a pas reçu de réponses."
        else:
            count = len(self.__replies)
            for response in self.__replies:
                concatenate += "Réponse n°" + count.__str__()
                count -= 1

                if response.author.name is not None:
                    author_name = response.author.name
                    if len(author_name) != 0:
                        concatenate += " par " + response.author.name
                if response.date is not None:
                    concatenate += " le " + response.date.strftime("%Y-%m-%d %H:%M:%S")

                try:
                    if response.response is not None:
                        concatenate += ".\n" + response.response.strip() + "\n"
                    else:
                        self.logger.error("No message in response " + self.id)
                except Exception as e:
                    self.logger.error(format(e))

        return concatenate

    def getColumnsForSQlite(self) -> {}:
        return {
            'NoSignalement': self.__id,
            'Auteur': self.__author,
            'Commune': self.__commune,
            'Insee': self.__insee,
            'Département': self.__departement,
            'Département_id': self.__departementId,
            'Date_création': self.__dateCreation,
            'Date_MAJ': self.__dateMaj,
            'Date_validation': self.__dateValidation,
            'Thèmes': self.__themes,
            'Statut': self.__statut,
            'Message': self.__message,
            'Réponses': self.__replies,
            'URL': self.__url,
            'URL_privé': self.__urlPrive,
            'Document': self.__attachments,
            'Autorisation': self.__autorisation,
            'geom': self.__geometry
        }

    def getStrAttachments(self, attachments) -> str:
        docs = ''
        if attachments is None or len(attachments) == 0:
            return docs
        for attachment in attachments:
            docs += "{} ".format(attachment['download_uri'])
        return docs[:-1]

    def setUrl(self, idReport) -> str:
        return "{0}/gcms/api/reports/{1}".format(self.__urlHostEspaceCo, idReport)

    def getStrThemes(self, themes) -> str:
        strThemes = ''
        if themes is None or len(themes) == 0:
            return strThemes
        for theme in themes:
            strThemes += "{},".format(theme)
        return strThemes[:-1]

    # TODO vérifier avec l'ancien code
    def getStrReplies(self, replies) -> str:
        strReplies = ''
        if replies is None or len(replies) == 0:
            return strReplies
        for replie in replies:
            strReplies += "{},".format(replies)
        return strReplies[:-1]