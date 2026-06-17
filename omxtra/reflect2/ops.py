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
