import typing as ta

from ..errors import ReflectionTypeError
from .types import CallableType
from .types import ProperType
from .types import Type
from .typevisitor import TypeTranslator


T = ta.TypeVar('T', bound=Type)


##


class TypeCopier(TypeTranslator):
    pass


@ta.overload
def copy_type(typ: CallableType) -> CallableType:
    ...


@ta.overload
def copy_type(typ: ProperType) -> ProperType:
    ...


@ta.overload
def copy_type(typ: T) -> T:
    ...


def copy_type(typ: T) -> T:
    copied = typ.accept(TypeCopier())
    if not isinstance(copied, type(typ)):
        raise ReflectionTypeError(copied)
    return copied


def copy_types(typs: ta.Iterable[T]) -> list[T]:
    return [copy_type(typ) for typ in typs]
