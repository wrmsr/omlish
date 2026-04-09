import typing as ta
import weakref


T = ta.TypeVar('T')
V = ta.TypeVar('V')


##


class TypeMap(ta.Generic[T]):
    def __init__(self, items: ta.Iterable[T] = ()) -> None:
        super().__init__()

        self._items = list(items)
        dct: dict[type, ta.Any] = {}
        for item in items:
            if (ty := type(item)) in dct:
                raise ValueError(ty)
            dct[ty] = item
        self._dct = dct

    @classmethod
    def of(cls, items: ta.Iterable[T]) -> TypeMap[T]:
        if isinstance(items, TypeMap):
            return items
        return cls(items)

    @property
    def items(self) -> ta.Sequence[T]:
        return self._items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._items)

    def __contains__(self, ty: type[T]) -> bool:
        return ty in self._items

    def get(self, ty: type[T]) -> T | None:
        return self._dct.get(ty)

    def __getitem__(self, ty: type[T]) -> T:
        return self._dct[ty]

    _any_dct: dict[type | tuple[type, ...], tuple[T, ...]]

    def get_any(self, cls: type | tuple[type, ...]) -> ta.Sequence[T]:
        try:
            any_dct = self._any_dct
        except AttributeError:
            any_dct = {}
            self._any_dct = any_dct

        try:
            return any_dct[cls]
        except KeyError:
            pass

        ret = tuple(tv for tv in self if isinstance(tv, cls))
        any_dct[cls] = ret
        return ret


class DynamicTypeMap(ta.Generic[V]):
    def __init__(self, items: ta.Iterable[V] = (), *, weak: bool = False) -> None:
        super().__init__()

        self._items = list(items)
        self._weak = bool(weak)

        self._cache: ta.MutableMapping[type, ta.Any] = weakref.WeakKeyDictionary() if weak else {}

    @property
    def items(self) -> ta.Sequence[V]:
        return self._items

    @property
    def is_weak(self) -> bool:
        return self._weak

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> ta.Iterator[V]:
        return iter(self._items)

    def __getitem__(self, ty: type[T]) -> ta.Sequence[T]:
        try:
            return self._cache[ty]
        except KeyError:
            ret = []
            for item in self._items:
                if isinstance(item, ty):
                    ret.append(item)
            self._cache[ty] = ret
            return ret
