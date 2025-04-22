# ruff: noqa: UP007
import typing as ta

from .values import TypedValue
from .values import UniqueTypedValue


TypedValueT = ta.TypeVar('TypedValueT', bound=TypedValue)
TypedValueU = ta.TypeVar('TypedValueU', bound=TypedValue)

UniqueTypedValueU = ta.TypeVar('UniqueTypedValueU', bound=UniqueTypedValue)


##


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
            default: None = None,
    ) -> UniqueTypedValueU | None:
        ...

    @ta.overload
    def pop(
            self,
            cls: type[TypedValueU],
            /,
            default: ta.Iterable[TypedValueU] | None = None,
    ) -> ta.Sequence[TypedValueU]:
        ...

    def pop(self, key, /, default=None):
        if not isinstance(key, type):
            if default is not None:
                raise RuntimeError('Must not provide both an instance key and a default')
            default = key
            key = type(default)

        return self._dct.pop(key, default)
