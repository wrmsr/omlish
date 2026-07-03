# ruff: noqa: SLF001
import typing as ta

from .core.subtypes import MroEntry
from .core.subtypes import get_mro_entries
from .core.symbols import TypeInfo
from .core.typeops import make_union
from .core.types import Instance
from .core.types import NoneType
from .core.types import Type
from .core.types import UnboundType
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
    if isinstance(robj, Type):
        if isinstance(robj, UnboundType):
            return robj._runtime_object

        if not isinstance(robj, Instance):
            return None

        robj = robj._type

    if not isinstance(robj, TypeInfo):
        raise TypeError(f'Expected TypeInfo or Type, got {type(robj).__name__}')

    return robj._runtime_object


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


def is_optional(rty: Type) -> bool:
    return isinstance(rty, UnionType) and any(isinstance(item, NoneType) for item in rty.items)


def strip_optional(rty: UnionType) -> Type:
    items = [
        item
        for item in rty.items
        if not isinstance(item, NoneType)
    ]
    if len(items) == 1:
        return items[0]
    return make_union(items)


##


def reflect_mro_entries(source: object, *, mirror: Mirror | None = None) -> ta.Sequence[MroEntry]:
    source_type = or_global_mirror(mirror).reflect_type(source)
    if not isinstance(source_type, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {source_type!r}')
    return get_mro_entries(source_type)


def reflect_mro_entries_by_info(obj: object, *, mirror: Mirror | None = None) -> dict[object, MroEntry]:
    return {
        entry._info: entry
        for entry in reflect_mro_entries(obj, mirror=mirror)
    }
