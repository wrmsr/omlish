# ruff: noqa: SLF001
import typing as ta

from .core.subtypes import MroEntry
from .core.subtypes import get_mro_entries
from .core.typeops import make_union
from .core.types import Instance
from .core.types import NoneType
from .core.types import Type
from .core.types import UnionType
from .errors import ReflectionTypeError


if ta.TYPE_CHECKING:
    from .mirror import Mirror


##


def reflect_mro_entries(
        source: object,
        *,
        mirror: Mirror,
) -> ta.Sequence[MroEntry]:
    source_type = mirror.reflect_type(source)
    if not isinstance(source_type, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {source_type!r}')
    return get_mro_entries(source_type)


def reflect_mro_entries_by_info(
        obj: object,
        *,
        mirror: Mirror,
) -> dict[object, MroEntry]:
    return {
        entry._info: entry
        for entry in reflect_mro_entries(obj, mirror=mirror)
    }


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
