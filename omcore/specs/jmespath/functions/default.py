from .base import FunctionsClass
from .container import ContainerFunctions
from .keyed import KeyedFunctions
from .number import NumberFunctions
from .object import ObjectFunctions
from .string import StringFunctions
from .type import TypeFunctions


##


class DefaultFunctions(
    KeyedFunctions,
    ObjectFunctions,
    StringFunctions,
    NumberFunctions,
    ContainerFunctions,
    TypeFunctions,
    FunctionsClass,
):
    pass
