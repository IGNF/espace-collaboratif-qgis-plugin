'''
Transformation d'une condition MongoDB en expression QGIS
'''
class MongoDBtoQGIS(object):
    # Condition en mongoDB
    condition = None

    # Les équivalences entre conditions mongoDB et expressions QGIS
    andCondition = {'$and': 'AND'}
    orCondition = {'$or': 'OR'}
    notCondition = {'$not': 'NOT'}
    operatorCondition = {
        '$gt': '>',
        '$gte': '>=',
        '$lt': '<',
        '$lte': '<=',
        '$eq': '=',
        '$ne': '<>',
        '$in': 'IN',
        '$nin': 'NOT IN',
        '$like': 'LIKE',
        '$nlike': 'NOT LIKE',
        '$regex': 'LIKE'
    }
    operatorConditionNull = {
        '$eq': 'IS',
        '$ne': 'IS NOT',
    }

    '''
    Intialisation de la classe avec la condition issue du collaboratif
    exemple : "{\"$and\":[{\"capacite\":{\"$lte\":5}}]}"
    '''
    def __init__(self, conditionMongoDB):
        self.condition = conditionMongoDB

