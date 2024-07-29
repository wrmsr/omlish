import functools
import itertools
import typing as ta

from .. import check
from .identity import IdentityKeyDict
from .identity import IdentitySet


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


def mut_toposort(data: dict[T, set[T]]) -> ta.Iterator[set[T]]:
    for k, v in data.items():
        v.discard(k)
    extra_items_in_deps = functools.reduce(set.union, data.values()) - set(data.keys())
    data.update({item: set() for item in extra_items_in_deps})
    while True:
        ordered = {item for item, dep in data.items() if not dep}
        if not ordered:
            break
        yield ordered
        data = {item: (dep - ordered) for item, dep in data.items() if item not in ordered}
    if data:
        raise ValueError('Cyclic dependencies exist among these items: ' + ' '.join(repr(x) for x in data.items()))


def toposort(data: ta.Mapping[T, ta.AbstractSet[T]]) -> ta.Iterator[set[T]]:
    return mut_toposort({k: set(v) for k, v in data.items()})


##


def partition(items: ta.Iterable[T], pred: ta.Callable[[T], bool]) -> tuple[list[T], list[T]]:
    t: list[T] = []
    f: list[T] = []
    for e in items:
        if pred(e):
            t.append(e)
        else:
            f.append(e)
    return t, f


def unique(it: ta.Iterable[T], *, identity: bool = False) -> list[T]:
    if isinstance(it, str):
        raise TypeError(it)
    ret: list[T] = []
    seen: ta.MutableSet[T] = IdentitySet() if identity else set()
    for e in it:
        if e not in seen:
            seen.add(e)
            ret.append(e)
    return ret


def unique_map(kvs: ta.Iterable[tuple[K, V]], *, identity: bool = False) -> ta.MutableMapping[K, V]:
    d: ta.MutableMapping[K, V] = IdentityKeyDict() if identity else {}
    for k, v in kvs:
        if k in d:
            raise KeyError(k)
        d[k] = v
    return d


def unique_map_by(fn: ta.Callable[[V], K], vs: ta.Iterable[V], *, identity: bool = False) -> ta.MutableMapping[K, V]:
    return unique_map(((fn(v), v) for v in vs), identity=identity)


def multi_map(kvs: ta.Iterable[tuple[K, V]], *, identity: bool = False) -> ta.MutableMapping[K, list[V]]:
    d: ta.MutableMapping[K, list[V]] = IdentityKeyDict() if identity else {}
    l: list[V]
    for k, v in kvs:
        try:
            l = d[k]
        except KeyError:
            l = d[k] = []
        l.append(v)
    return d


def multi_map_by(fn: ta.Callable[[V], K], vs: ta.Iterable[V], *, identity: bool = False) -> ta.MutableMapping[K, list[V]]:  # noqa
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


def mut_unify_sets(sets: ta.Iterable[set[T]]) -> list[set[T]]:
    rem: list[set[T]] = list(sets)
    ret: list[set[T]] = []
    while rem:
        cur = rem.pop()
        while True:
            moved = False
            for i in range(len(rem) - 1, -1, -1):
                if any(e in cur for e in rem[i]):
                    cur.update(rem.pop(i))
                    moved = True
            if not moved:
                break
        ret.append(cur)
    if ret:
        all_ = set(itertools.chain.from_iterable(ret))
        num = sum(map(len, ret))
        check.equal(len(all_), num)
    return ret
