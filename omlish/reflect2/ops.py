# ruff: noqa: SLF001
import typing as ta

from .core.subtypes import MroEntry
from .core.subtypes import get_mro_entries
from .core.symbols import TypeInfo
from .core.typeops import make_union
from .core.types import AnyType
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

        if isinstance(robj, NoneType):
            return type(None)

        if isinstance(robj, AnyType):
            return ta.Any

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


##


class Mro(ta.Sequence[MroEntry]):
    def __init__(self, entries: ta.Iterable[MroEntry]) -> None:
        super().__init__()

        self._seq = tuple(entries)

    #

    def __len__(self) -> int:
        return len(self._seq)

    def __iter__(self) -> ta.Iterator[MroEntry]:
        return iter(self._seq)

    def __contains__(self, entry: object) -> bool:
        return entry in self._seq

    @ta.overload
    def __getitem__(self, index: int, /) -> MroEntry: ...

    @ta.overload
    def __getitem__(self, index: slice, /) -> ta.Sequence[MroEntry]: ...

    def __getitem__(self, index, /):
        return self._seq[index]

    #

    _by_info: ta.Mapping[TypeInfo, MroEntry]

    @property
    def by_info(self) -> ta.Mapping[TypeInfo, MroEntry]:
        try:
            return self._by_info
        except AttributeError:
            pass

        dct = {entry._info: entry for entry in self._seq}
        self._by_info = dct
        return dct


def get_mro(rty: Type) -> Mro:
    if not isinstance(rty, Instance):
        raise ReflectionTypeError(f'Unsupported MRO source: {rty!r}')
    return Mro(get_mro_entries(rty))
