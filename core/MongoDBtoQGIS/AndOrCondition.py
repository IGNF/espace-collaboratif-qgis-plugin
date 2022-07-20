from .AbstractCondition import *


class AndOrCondition(AbstractCondition):
    def __init__(self, operator, sub_conditions):
        self._operator = operator
        self._sub_conditions = sub_conditions

    def toSQL(self):
        and_parts = []
        if len(self._sub_conditions) == 1:
            and_parts.append("{}".format(self._sub_conditions[0].toSQL()))
        else:
            for sub_condition in self._sub_conditions:
                and_parts.append("({})".format(sub_condition.toSQL()))

        glue = " AND " if "$and" == self._operator else " OR "
        return glue.join(and_parts)
