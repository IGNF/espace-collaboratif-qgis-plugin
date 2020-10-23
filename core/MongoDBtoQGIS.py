'''
Transformation d'une condition MongoDB en expression QGIS
'''
class MongoDBtoQGIS(object):
    # Condition en mongoDB
    condition = None

    # Les équivalences entre conditions mongoDB et expressions QGIS
    conditions = {'$and': 'AND', '$or': 'OR', '$not': 'NOT'}
    operatorCondition = {
        '$gt': '>',
        '$gte': '>=',
        '$lt': '<',
        '$lte': '<=',
        '$eq': '=',
        ':': '=',
        '$ne': '<>',
        '$in': 'IN',
        '$nin': 'NOT IN',
        '$like': 'LIKE',
        '$nlike': 'NOT LIKE',
        '$regex': 'LIKE'
    }
    operatorConditionNull = {
        ':$eq:': 'IS',
        ':$ne:': 'IS NOT',
    }

    '''
    Intialisation de la classe avec la condition issue du collaboratif
    exemple : "{\"$and\":[{\"capacite\":{\"$lte\":5}}]}"
    '''
    def __init__(self, conditionMongoDB):
        self.condition = conditionMongoDB

    def numberOfOccurrences(self, searchTo, substring):
        return substring.count(searchTo)

    def conversionOperator(self, op):
        return self.operatorCondition[op]

    def replaceSomeCharacters(self, substring, listOfCharacters):
        newString = substring
        for c, v in listOfCharacters.items():
            newString = newString.replace(c, v)
        return newString

    def run(self):
        print(self.condition)
        d = {' ': '', '{': '', '}': '', '"': ''}
        chaine = self.replaceSomeCharacters(self.condition, d)
        print(chaine)
        nb = self.numberOfOccurrences('[', chaine)
        if nb == 1:
            dd = {':[': ',', ']': ''}
            tmp = self.replaceSomeCharacters(chaine, dd)
            print(tmp)
            nb_parts = tmp.split(',')
            for part in nb_parts:
                if type(part) is str:
                    operateur = self.conditions[part]
                    print(operateur)

                if type(part) is dict:
                    print(part)



