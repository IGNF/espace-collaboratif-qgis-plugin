"""
Transformation d'une condition MongoDB en expression QGIS, exemples :

"{\"$or\":[{\"$and\":[{\"choix\":\"choix 1\"},{\"entier\":{\"$lt\":5}}]},{\"double\":{\"$ne\":null}}]}"
("choix" = 'choix 1' AND "entier" < 5) OR "double" is not null

{\"$and\":[{\"string\":\"Cantine\"}]}
"string" = 'Cantine'

{\"$or\":[{\"date\":{\"$gt\":\"2020-09-01\"}},{\"boolean\":1}]}
"date" > '2020-09-01' OR "boolean" = '1'
"""


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

    def conversionConditions(self, condition):
        return self.conditions[condition]

    def conversionOperatorCondition(self, operator):
        return self.operatorCondition[operator]

    def conversionOperatorConditionNull(self, operator):
        return self.operatorConditionNull[operator]

    def replaceSomeCharacters(self, substring, listOfCharacters):
        newString = substring
        for c, v in listOfCharacters.items():
            newString = newString.replace(c, v)
        return newString

    def setExpression(self, partOne, operator, partTwo):
        return "\"{}\" {} '{}'".format(partOne, operator, partTwo)

    def run(self):
        d = {'{': '', '}': '', '"': ''}
        chaine = self.replaceSomeCharacters(self.condition, d)
        dd = {' : ': ':'}
        chaine = self.replaceSomeCharacters(chaine, dd)
        nbCrochetOuvrant = self.numberOfOccurrences('[', chaine)

        if nbCrochetOuvrant == 1:
            dd = {':[': ',', ']': ''}
            tmp = self.replaceSomeCharacters(chaine, dd)
            nb_parts = tmp.split(',')
            orAndNot = None
            expression = None
            i = 0
            for part in nb_parts:
                nbTwoPoints = self.numberOfOccurrences(':', part)
                if nbTwoPoints == 0:
                    orAndNot = self.conversionConditions(part)
                elif nbTwoPoints == 1:
                    part_twoPoints = part.split(':')
                    operator = self.conversionOperatorCondition(':')
                    tmp = self.setExpression(part_twoPoints[0], operator, part_twoPoints[1])
                    if i == 1:
                        expression = "{}".format(tmp)
                    else:
                        expression += " {} {}".format(orAndNot, tmp)
                elif nbTwoPoints == 2:
                    part_twoPoints = part.split(':')
                    operator = self.conversionOperatorCondition(part_twoPoints[1])
                    tmp = self.setExpression(part_twoPoints[0], operator, part_twoPoints[2])
                    if i == 1:
                        expression = "{}".format(tmp)
                    else:
                        expression += " {} {}".format(orAndNot, tmp)
                i = i + 1
            return expression
        elif nbCrochetOuvrant > 1:
            # $or:[$and:[choix:choix 1,entier:$lt:5],double:$ne:null]
            return ''

