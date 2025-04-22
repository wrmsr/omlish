# ruff: noqa: UP007
import dataclasses as dc
import typing as ta

from .. import lang
from .values import TypedValue
from .values import UniqueTypedValue


TypedValueT = ta.TypeVar('TypedValueT', bound=TypedValue)
TypedValueU = ta.TypeVar('TypedValueU', bound=TypedValue)

UniqueTypedValueU = ta.TypeVar('UniqueTypedValueU', bound=UniqueTypedValue)


##


@dc.dataclass()
class UnconsumedTypedValuesError(Exception):
    values: ta.Sequence[TypedValue]


class _NOT_SET(lang.Marker):  # noqa
    pass


class TypedValuesConsumer(ta.Generic[TypedValueT]):
    def __init__(
            self,
            src: ta.Union[
                ta.Iterable[tuple[type[TypedValueT], TypedValueT | tuple[TypedValueT, ...]]],
                ta.Mapping[type[TypedValueT], TypedValueT | tuple[TypedValueT, ...]],
            ],
    ) -> None:
        super().__init__()

        self._dct = dict(src)

    #

    def check_empty(self) -> None:
        if bool(self._dct):
            raise UnconsumedTypedValuesError(list(self))

    def __enter__(self) -> 'TypedValuesConsumer[TypedValueT]':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.check_empty()

    #

    def __iter__(self) -> ta.Iterator[TypedValueT]:
        for v in self._dct.values():
            if isinstance(v, tuple):
                yield from v
            else:
                yield v

    def __len__(self) -> int:
        return len(self._dct)

    def __bool__(self) -> bool:
        return bool(self._dct)

    #

    def keys(self) -> ta.KeysView[type[TypedValueT]]:
        return self._dct.keys()

    def values(self) -> ta.ValuesView[TypedValueT | tuple[TypedValueT, ...]]:
        return self._dct.values()

    def items(self) -> ta.ItemsView[type[TypedValueT], TypedValueT | tuple[TypedValueT, ...]]:
        return self._dct.items()

    #

    @ta.overload
    def pop(
            self,
            tv: UniqueTypedValueU,
    ) -> UniqueTypedValueU:
        ...

    @ta.overload
    def pop(
            self,
            cls: type[UniqueTypedValueU],
            /,
            default: UniqueTypedValueU,
    ) -> UniqueTypedValueU:
        ...

    @ta.overload
    def pop(  # type: ignore[overload-overlap]
            self,
            cls: type[UniqueTypedValueU],
            /,
            default: UniqueTypedValueU | None = None,
    ) -> UniqueTypedValueU | None:
        ...

    @ta.overload
    def pop(
            self,
            cls: type[TypedValueU],
    ) -> ta.Sequence[TypedValueU]:
        ...

    @ta.overload
    def pop(
            self,
            cls: type[TypedValueU],
            /,
            default: ta.Iterable[TypedValueU],
    ) -> ta.Sequence[TypedValueU]:
        ...

    @ta.overload
    def pop(
            self,
            cls: type[TypedValueU],
            /,
            default: ta.Iterable[TypedValueU] | None,
    ) -> ta.Sequence[TypedValueU] | None:
        ...

    def pop(self, key, /, default=_NOT_SET):
        if not isinstance(key, type):
            if default is not _NOT_SET:
                raise RuntimeError('Must not provide both an instance key and a default')
            default = key
            key = type(default)

        try:
            return self._dct.pop(key)
        except KeyError:
            if default is not _NOT_SET:
                return default
            else:
                raise
