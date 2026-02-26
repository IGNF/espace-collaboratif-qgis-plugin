import json
from .AndOrCondition import AndOrCondition
from .OperatorCondition import OperatorCondition


class ConditionFactory:
    def __init__(self):
        pass

    def create_condition(self, condition):
        if condition is None:
            return None

        if type(condition) is str:
            js = json.loads(condition)
        else:
            js = condition

        sub_conditions = []
        for key, value in js.items():
            if key in ("$and", "$or"):
                sub_condition = self.create_andor_condition(key, value)
            # elif "$not" == key: TODO
            else:
                sub_condition = OperatorCondition(key, value)

            sub_conditions.append(sub_condition)

        if len(sub_conditions) > 1:
            return AndOrCondition("$and", sub_conditions[0])
        else:
            return sub_conditions[0]

    def create_andor_condition(self, operator, conditions):
        sub_conditions = []
        for condition in conditions:
            for key, value in condition.items():
                if value is None or type(value) in (str, int, float, bool):
                    value = {"$eq": value}

                sub_condition = self.create_condition({key: value})
                sub_conditions.append(sub_condition)

        return AndOrCondition(operator, sub_conditions)
