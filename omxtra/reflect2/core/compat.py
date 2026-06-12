from ..errors import UnsupportedTypeOperationError
from .subtypes import is_subtype
from .types import Type


##


def is_assignable(source: Type, target: Type) -> bool:
    return is_subtype(source, target)


def is_assignable_or_false(source: Type, target: Type) -> bool:
    try:
        return is_assignable(source, target)
    except UnsupportedTypeOperationError:
        return False
