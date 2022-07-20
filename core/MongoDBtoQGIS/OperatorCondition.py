import re
from .AbstractCondition import *


class OperatorCondition(AbstractCondition):
    KEY_GREATERTHAN = '$gt'
    KEY_GREATERTHANEQUAL = '$gte'
    KEY_LESSTHAN = '$lt'
    KEY_LESSTHANEQUAL = '$lte'
    KEY_EQUAL = '$eq'
    KEY_NOT_EQUAL = '$ne'
    KEY_IN = '$in'
    KEY_NOT_IN = '$nin'
    KEY_REGEX = '$regex'

    KEYS_TO_OPERATORS = {
        '$gt': '>',
        '$gte': '>=',
        '$lt': '<',
        '$lte': '<=>',
        '$eq': '=',
        '$ne': '<>',
        '$in': 'IN',
        '$nin': 'NOT IN',
        '$like': 'LIKE',
        '$nlike': 'NOT LIKE',
        '$regex': 'LIKE'
    }

    def __init__(self, key, value):
        self._key = key
        self._value = value

    def quote(self, value):
        if str is None:
            return "''"
        return "'{}'".format(value)

    def toSQL(self):
        sql = None

        # exemple {"$regex": "^test","$options":"i"}}
        # keys : "$regex" et "$options"
        keys = list(self._value.keys())

        operator = keys[0]
        if operator not in self.KEYS_TO_OPERATORS:
            return None

        option = None
        if len(keys) == 2 and '$options' == keys[1]:
            option = self._value['$options']

        sql_operator = self.KEYS_TO_OPERATORS[operator]
        sql_value = self._value[operator]

        if operator in (
                self.KEY_GREATERTHAN, self.KEY_GREATERTHANEQUAL, self.KEY_LESSTHAN, self.KEY_LESSTHANEQUAL,
                self.KEY_EQUAL,
                self.KEY_NOT_EQUAL):
            if sql_value is not None:
                sql = "{} {} {}".format(self.quote(self._key), sql_operator, self.quote(sql_value))
            elif operator == self.KEY_EQUAL:
                sql = "'{}' IS NULL".format(self._key)
            elif operator == self.KEY_NOT_EQUAL:
                sql = "'{}' IS NOT NULL".format(self._key)
        elif operator in (self.KEY_IN, self.KEY_NOT_IN):
            if type(sql_value) is not list:
                return None

            iterator = map(self.quote, sql_value)
            values = ",".join(list(iterator))
            sql = "{} {} ({})".format(self.quote(self._key), sql_operator, values)
        elif operator == self.KEY_REGEX:
            sql = self.get_sql_from_regex(sql_value, option)

        return sql

    def get_sql_from_regex(self, regex_str, option):
        match = re.search(r"\^([\w -\']+)\$", regex_str)
        if match:
            operator = "LIKE" if option is None else "ILIKE"
            return "{} {} {}".format(self.quote(self._key), operator, self.quote(match.group(1)))

        operator = "NOT LIKE" if option is None else "NOT ILIKE"

        # pas egal
        match = re.search(r"\^\(\?\!([\w -\']+)\$\)\.\*\$", regex_str)
        if match:
            return "{} {} {}".format(self.quote(self._key), operator, self.quote(match.group(1)))

        # ne contient pas
        match = re.search(r"\^\(\(\?\!([\w -\']+)\)\.\)\*\$", regex_str)
        if match:
            return "{} {} {}".format(self.quote(self._key), operator, self.quote(match.group(1)))

        # ne finit pas par
        match = re.search(r"\(\?\<\!([\w -\']+)\)\$", regex_str)
        if match:
            return "{} {} {}".format(self.quote(self._key), operator, self.quote("%{}".format(match.group(1))))

        # finit par
        match = re.search(r"([\w -\']+)\$", regex_str)
        if match:
            operator = "LIKE" if option is None else "ILIKE"
            return "{} {} {}".format(self.quote(self._key), operator, self.quote("%{}".format(match.group(1))))

        # ne commence pas par
        match = re.search(r"\^\(\?\!([\w -\']+)\)", regex_str)
        if match:
            operator = "NOT LIKE" if option is None else "NOT ILIKE"
            return "{} {} {}".format(self.quote(self._key), operator, self.quote("{}%".format(match.group(1))))

        # commence par
        match = re.search(r"\^([\w -\']+)", regex_str)
        if match:
            operator = "LIKE" if option is None else "ILIKE"
            return "{} {} {}".format(self.quote(self._key), operator, self.quote("{}%".format(match.group(1))))

        operator = "LIKE" if option is None else "ILIKE"
        return "{} {} {}".format(self.quote(self._key), operator, self.quote("%{}%".format(match.group(1))))

    @staticmethod
    def key_list():
        return list(OperatorCondition.KEYS_TO_OPERATORS.keys())
