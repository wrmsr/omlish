import typing as ta
import weakref


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


def multikey_dict(dct: ta.Mapping[ta.Iterable[K] | K, V], *, deep: bool = False) -> dict[K, V]:
    ret = {}
    for k, v in dct.items():
        if deep and isinstance(v, dict):
            v = multikey_dict(v, deep=True)  # type: ignore
        if isinstance(k, tuple):
            for sk in k:
                ret[sk] = v
        else:
            ret[k] = v
    return ret


def guarded_map_update(
        dst: ta.MutableMapping[ta.Any, ta.Any],
        *srcs: ta.Mapping[ta.Any, ta.Any],
) -> ta.MutableMapping[ta.Any, ta.Any]:
    for src in srcs:
        for k, v in src.items():
            if k in dst:
                raise KeyError(k)
            dst[k] = v
    return dst


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

    @property
    def items(self) -> ta.Sequence[T]:
        return self._items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._items)

    def get(self, ty: type[T]) -> T | None:
        return self._dct.get(ty)

    def __getitem__(self, ty: type[T]) -> ta.Sequence[T]:
        return self._dct[ty]


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
    def weak(self) -> bool:
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


class MissingDict(dict[K, V]):
    def __init__(self, missing_fn: ta.Callable[[K], V]) -> None:
        if not callable(missing_fn):
            raise TypeError(missing_fn)
        super().__init__()
        self._missing_fn = missing_fn

    def __missing__(self, key):
        v = self[key] = self._missing_fn(key)
        return v
