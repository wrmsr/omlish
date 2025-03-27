import typing as ta

from .. import check
from .frozen import FrozenDict
from .frozen import FrozenList


T = ta.TypeVar('T')
T2 = ta.TypeVar('T2')
K = ta.TypeVar('K')
K2 = ta.TypeVar('K2')
V = ta.TypeVar('V')
V2 = ta.TypeVar('V2')


##


def _unpack_fn(fn):
    if isinstance(fn, tuple):
        return check.of_isinstance(fn)
    elif isinstance(fn, type) or callable(fn):
        return fn
    else:
        raise TypeError(fn)


# region seq


def seq(
        it: ta.Iterable[T],
) -> ta.Sequence[T]:
    if isinstance(it, str):
        raise TypeError(it)
    elif isinstance(it, FrozenList):
        return it
    else:
        return FrozenList(it)


def opt_seq(
        it: ta.Iterable[T] | None,
) -> ta.Sequence[T] | None:
    if it is None:
        return None
    else:
        return seq(it)


def seq_or_none(
        it: ta.Iterable[T] | None,
) -> ta.Sequence[T] | None:
    ret = opt_seq(it)
    if ret:
        return ret
    else:
        return None


def seq_of(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T]], ta.Sequence[T2]]:
    def inner(it):
        return seq(fn(e) for e in it)  # type: ignore

    fn = _unpack_fn(fn)
    return inner


def opt_seq_of(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T] | None], ta.Sequence[T2] | None]:
    def inner(it):
        if it is None:
            return None
        else:
            return seq(fn(e) for e in it)  # type: ignore

    fn = _unpack_fn(fn)
    return inner


def seq_of_or_none(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T] | None], ta.Sequence[T2] | None]:
    def inner(it):
        if it is None:
            return None
        else:
            ret = seq(fn(e) for e in it)  # type: ignore
            if ret:
                return ret
            else:
                return None

    fn = _unpack_fn(fn)
    return inner


# endregion


# region abs_set


def abs_set(
        it: ta.Iterable[T],
) -> ta.AbstractSet[T]:
    if isinstance(it, str):
        raise TypeError(it)
    elif isinstance(it, frozenset):
        return it
    else:
        return frozenset(it)


def opt_abs_set(
        it: ta.Iterable[T] | None,
) -> ta.AbstractSet[T] | None:
    if it is None:
        return None
    else:
        return abs_set(it)


def abs_set_or_none(
        it: ta.Iterable[T] | None,
) -> ta.AbstractSet[T] | None:
    ret = opt_abs_set(it)
    if ret:
        return ret
    else:
        return None


def abs_set_of(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T]], ta.AbstractSet[T2]]:
    def inner(it):
        return abs_set(fn(e) for e in it)  # type: ignore

    fn = _unpack_fn(fn)
    return inner


def opt_abs_set_of(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T] | None], ta.AbstractSet[T2] | None]:
    def inner(it):
        if it is None:
            return None
        else:
            return abs_set(fn(e) for e in it)  # type: ignore

    fn = _unpack_fn(fn)
    return inner


def abs_set_of_or_none(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T] | None], ta.AbstractSet[T2] | None]:
    def inner(it):
        if it is None:
            return None
        else:
            ret = abs_set(fn(e) for e in it)  # type: ignore
            if ret:
                return ret
            else:
                return None

    fn = _unpack_fn(fn)
    return inner


# endregion


# region frozenset


def frozenset_(
        it: ta.Iterable[T],
) -> frozenset[T]:
    if isinstance(it, str):
        raise TypeError(it)
    elif isinstance(it, frozenset):
        return it
    else:
        return frozenset(it)


def opt_frozenset(
        it: ta.Iterable[T] | None,
) -> frozenset[T] | None:
    if it is None:
        return None
    else:
        return frozenset_(it)


def frozenset_or_none(
        it: ta.Iterable[T] | None,
) -> frozenset[T] | None:
    ret = opt_frozenset(it)
    if ret:
        return ret
    else:
        return None


def frozenset_of(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T]], frozenset[T2]]:
    def inner(it):
        return frozenset_(fn(e) for e in it)  # type: ignore

    fn = _unpack_fn(fn)
    return inner


def opt_frozenset_of(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T] | None], frozenset[T2] | None]:
    def inner(it):
        if it is None:
            return None
        else:
            return frozenset_(fn(e) for e in it)  # type: ignore

    fn = _unpack_fn(fn)
    return inner


def frozenset_of_or_none(
        fn: ta.Callable[[T], T2] | tuple,
) -> ta.Callable[[ta.Iterable[T] | None], frozenset[T2] | None]:
    def inner(it):
        if it is None:
            return None
        else:
            ret = frozenset_(fn(e) for e in it)  # type: ignore
            if ret:
                return ret
            else:
                return None

    fn = _unpack_fn(fn)
    return inner


# endregion


# region map


def map(  # noqa
        src: ta.Mapping[K, V] | ta.Iterable[tuple[K, V]],
) -> ta.Mapping[K, V]:
    return FrozenDict(src)


def opt_map(
        src: ta.Mapping[K, V] | ta.Iterable[tuple[K, V]] | None,
) -> ta.Mapping[K, V] | None:
    if src is None:
        return None
    else:
        return map(src)


def map_or_none(
        src: ta.Mapping[K, V] | ta.Iterable[tuple[K, V]] | None,
) -> ta.Mapping[K, V] | None:
    ret = opt_map(src)
    if ret:
        return ret
    else:
        return None


def map_of(
        key_fn: ta.Callable[[K], K2] | tuple,
        value_fn: ta.Callable[[V], V2] | tuple,
) -> ta.Callable[
    [ta.Mapping[K, V] | ta.Iterable[tuple[K, V]]],
    ta.Mapping[K2, V2],
]:
    def inner(src):
        return map((key_fn(k), value_fn(v)) for k, v in dict(src).items())  # type: ignore

    key_fn = _unpack_fn(key_fn)
    value_fn = _unpack_fn(value_fn)
    return inner


def opt_map_of(
        key_fn: ta.Callable[[K], K2] | tuple,
        value_fn: ta.Callable[[V], V2] | tuple,
) -> ta.Callable[
    [ta.Mapping[K, V] | ta.Iterable[tuple[K, V]] | None],
    ta.Mapping[K2, V2] | None,
]:
    def inner(src):
        if src is None:
            return None
        else:
            return map((key_fn(k), value_fn(v)) for k, v in dict(src).items())  # type: ignore

    key_fn = _unpack_fn(key_fn)
    value_fn = _unpack_fn(value_fn)
    return inner


def map_of_or_none(
        key_fn: ta.Callable[[K], K2] | tuple,
        value_fn: ta.Callable[[V], V2] | tuple,
) -> ta.Callable[
    [ta.Mapping[K, V] | ta.Iterable[tuple[K, V]] | None],
    ta.Mapping[K2, V2] | None,
]:
    def inner(src):
        if src is None:
            return None
        else:
            ret = map((key_fn(k), value_fn(v)) for k, v in dict(src).items())  # type: ignore
            if ret:
                return ret
            else:
                return None

    key_fn = _unpack_fn(key_fn)
    value_fn = _unpack_fn(value_fn)
    return inner


# endregion
