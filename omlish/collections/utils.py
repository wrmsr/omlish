import typing as ta

from .. import lang
from .identity import IdentityKeyDict
from .identity import IdentitySet


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class PartitionResult(ta.NamedTuple, ta.Generic[T]):
    t: list[T]
    f: list[T]


def partition(items: ta.Iterable[T], pred: ta.Callable[[T], bool]) -> PartitionResult[T]:
    t: list[T] = []
    f: list[T] = []
    for e in items:
        if pred(e):
            t.append(e)
        else:
            f.append(e)
    return PartitionResult(t, f)


##


def unique(
        it: ta.Iterable[T],
        *,
        key: ta.Callable[[T], ta.Any] = lang.identity,
        identity: bool = False,
        strict: bool = False,
) -> list[T]:
    if isinstance(it, str):
        raise TypeError(it)
    ret: list[T] = []
    seen: ta.MutableSet = IdentitySet() if identity else set()
    for e in it:
        k = key(e)
        if k in seen:
            if strict:
                raise lang.DuplicateKeyError(k, e)
        else:
            seen.add(k)
            ret.append(e)
    return ret


##


@ta.overload
def make_map(
        kvs: ta.Iterable[tuple[K, V]],
        *,
        identity: ta.Literal[False] = False,
        strict: bool = False,
) -> dict[K, V]:
    ...


@ta.overload
def make_map(
        kvs: ta.Iterable[tuple[K, V]],
        *,
        identity: bool = False,
        strict: bool = False,
) -> ta.MutableMapping[K, V]:
    ...


def make_map(
        kvs,
        *,
        identity=False,
        strict=False,
):
    d: ta.MutableMapping = IdentityKeyDict() if identity else {}
    for k, v in kvs:
        if k in d:
            if strict:
                raise lang.DuplicateKeyError(k)
        else:
            d[k] = v
    return d


#


@ta.overload
def make_map_by(
        fn: ta.Callable[[V], K],
        vs: ta.Iterable[V],
        *,
        identity: ta.Literal[False] = False,
        strict: bool = False,
) -> dict[K, V]:
    ...


@ta.overload
def make_map_by(
        fn: ta.Callable[[V], K],
        vs: ta.Iterable[V],
        *,
        identity: bool = False,
        strict: bool = False,
) -> ta.MutableMapping[K, V]:
    ...


def make_map_by(
        fn,
        vs,
        *,
        identity=False,
        strict=False,
):
    return make_map(
        ((fn(v), v) for v in vs),
        identity=identity,
        strict=strict,
    )


##


@ta.overload
def multi_map(
        kvs: ta.Iterable[tuple[K, V]],
        *,
        identity: ta.Literal[False] = False,
) -> dict[K, list[V]]:
    ...


@ta.overload
def multi_map(
        kvs: ta.Iterable[tuple[K, V]],
        *,
        identity: bool = False,
) -> ta.MutableMapping[K, list[V]]:
    ...


def multi_map(
        kvs,
        *,
        identity=False,
):
    d: ta.MutableMapping = IdentityKeyDict() if identity else {}
    for k, v in kvs:
        try:
            l = d[k]
        except KeyError:
            l = d[k] = []
        l.append(v)
    return d


#


@ta.overload
def multi_map_by(
        fn: ta.Callable[[V], K],
        vs: ta.Iterable[V],
        *,
        identity: ta.Literal[False] = False,
) -> dict[K, list[V]]:  # noqa
    ...


@ta.overload
def multi_map_by(
        fn: ta.Callable[[V], K],
        vs: ta.Iterable[V],
        *,
        identity: bool = False,
) -> ta.MutableMapping[K, list[V]]:  # noqa
    ...


def multi_map_by(
        fn,
        vs,
        *,
        identity=False,
):
    return multi_map(((fn(v), v) for v in vs), identity=identity)


##


def all_equal(it: ta.Iterable[T]) -> bool:
    i = iter(it)
    try:
        l = next(i)
    except StopIteration:
        return True
    return all(r == l for r in i)


def all_not_equal(it: ta.Iterable[T]) -> bool:
    s = set()
    for v in it:
        if v in s:
            return False
        s.add(v)
    return True


##


def key_cmp(fn: ta.Callable[[K, K], int]) -> ta.Callable[[tuple[K, V], tuple[K, V]], int]:
    return lambda t0, t1: fn(t0[0], t1[0])


def indexes(it: ta.Iterable[T]) -> dict[T, int]:
    return {e: i for i, e in enumerate(it)}
