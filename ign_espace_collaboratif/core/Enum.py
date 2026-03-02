"""
Taken from http://code.activestate.com/recipes/413486-first-class-enums-in-python/
(released under PSF license)
"""


def Enum(*names):
    # assert names, "Empty enums are not supported" # <- Don't like empty enums? Uncomment!

    class EnumClass(object):
        __slots__ = names

        def __iter__(self):
            return iter(constants)

        def __len__(self):
            return len(constants)

        def __getitem__(self, i):
            return constants[i]

        def __repr__(self):
            return 'Enum' + str(names)

        def __str__(self):
            return 'enum ' + str(constants)

    class EnumValue(object):
        __slots__ = '__value'

        def __init__(self, value): self.__value = value

        Value = property(lambda self: self.__value)
        EnumType = property(lambda self: EnumType)

        def __hash__(self):
            return hash(self.__value)

        def __invert__(self):
            return constants[maximum - self.__value]

        def __bool__(self):
            return bool(self.__value)

        def __repr__(self):
            return str(names[self.__value])

    maximum = len(names) - 1
    constants = [None] * len(names)
    for i, each in enumerate(names):
        val = EnumValue(i)
        setattr(EnumClass, each, val)
        constants[i] = val
    constants = tuple(constants)
    EnumType = EnumClass()
    return EnumType

    def __init__(self, params):
        """ Constructor """
