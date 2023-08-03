import collections.abc
import typing as ta
import weakref


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


def multikey_dict(dct: ta.Mapping[ta.Union[ta.Iterable[K], K], V], *, deep: bool = False) -> dict[K, V]:
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
        *srcs: ta.Mapping[ta.Any, ta.Any]
) -> ta.MutableMapping[ta.Any, ta.Any]:
    for src in srcs:
        for k, v in src.items():
            if k in dst:
                raise KeyError(k)
            dst[k] = v
    return dst


def yield_dict_init(*args, **kwargs) -> ta.Iterable[ta.Tuple[ta.Any, ta.Any]]:
    if len(args) > 1:
        raise TypeError
    if args:
        [src] = args
        if isinstance(src, collections.abc.Mapping):
            for k in src:
                yield (k, src[k])
        else:
            for k, v in src:
                yield (k, v)
    for k, v in kwargs.items():
        yield (k, v)


class ItemSeqTypeMap(ta.Generic[T]):

    def __init__(self, items: ta.Iterable[T], *, weak: bool = False) -> None:
        super().__init__()

        self._items = list(items)
        self._weak = bool(weak)

        self._cache: ta.MutableMapping[ta.Type[T], ta.Sequence[T]] = \
            weakref.WeakKeyDictionary() if weak else {}  # type: ignore

    @property
    def items(self) -> ta.Sequence[T]:
        return self._items

    @property
    def weak(self) -> bool:
        return self._weak

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> ta.Iterable[T]:
        return iter(self._items)

    def __getitem__(self, cls: ta.Type[T]) -> ta.Sequence[T]:
        try:
            return self._cache[cls]
        except KeyError:
            ret = []
            for item in self._items:
                if isinstance(item, cls):
                    ret.append(item)
            self._cache[cls] = ret
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
