# ruff: noqa: SLF001
import typing as ta

from .core.subtypes import MroEntry
from .core.subtypes import get_mro_entries
from .core.types import Instance
from .errors import ReflectionTypeError


if ta.TYPE_CHECKING:
    from .reflector import TypeReflector


##


def reflect_mro_entries(
        source: object,
        *,
        reflector: TypeReflector,
) -> ta.Sequence[MroEntry]:
    source_type = reflector.reflect_type(source)
    if not isinstance(source_type, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {source_type!r}')
    return get_mro_entries(source_type)


def reflect_mro_entries_by_info(
        obj: object,
        *,
        reflector: TypeReflector,
) -> dict[object, MroEntry]:
    return {
        entry._info: entry
        for entry in reflect_mro_entries(obj, reflector=reflector)
    }
