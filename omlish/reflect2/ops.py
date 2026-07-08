# ruff: noqa: SLF001
import typing as ta

from .core.symbols import TypeInfo
from .core.typeops import make_union
from .core.types import NoneType
from .core.types import Type
from .core.types import UnionType
from .errors import ReflectionTypeError
from .globals import or_global_mirror


if ta.TYPE_CHECKING:
    from .mirror import Mirror


##


def typeof(obj: object, *, mirror: Mirror | None = None) -> Type:
    try:
        cls = getattr(obj, '__orig_class__')
    except AttributeError:
        cls = type(obj)
    return or_global_mirror(mirror).reflect_type(cls)


##


def get_runtime_object_or_none(robj: Type | TypeInfo) -> object | None:
    if not isinstance(robj, (Type, TypeInfo)):
        raise TypeError(f'Expected TypeInfo or Type, got {type(robj).__name__}')
    return robj.runtime_object


def get_runtime_object(robj: Type | TypeInfo) -> object:
    ty = get_runtime_object_or_none(robj)
    if ty is None:
        raise ReflectionTypeError(f'No runtime object available for {robj!r}')
    return ty


def get_runtime_type_or_none(robj: Type | TypeInfo) -> type | None:
    obj = get_runtime_object_or_none(robj)
    return obj if isinstance(obj, type) else None


def get_runtime_type(robj: Type | TypeInfo) -> type:
    ty = get_runtime_type_or_none(robj)
    if ty is None:
        raise ReflectionTypeError(f'No runtime type available for {robj!r}')
    return ty


##


def _is_optional(rty: UnionType) -> bool:
    return any(isinstance(item, NoneType) for item in rty._items)


def is_optional(rty: Type) -> bool:
    return isinstance(rty, UnionType) and _is_optional(rty)


def strip_optional(rty: Type) -> Type:
    if not isinstance(rty, UnionType) or not _is_optional(rty):
        return rty

    items = [
        item
        for item in rty._items
        if not isinstance(item, NoneType)
    ]
    if len(items) == 1:
        return items[0]
    return make_union(items)
