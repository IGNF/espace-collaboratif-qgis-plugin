from abc import ABC, abstractmethod


class AbstractCondition(ABC):
    @abstractmethod
    def toSQL(self):
        pass
