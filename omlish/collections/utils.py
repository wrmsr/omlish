import functools
import typing as ta

from .identity import IdentityKeyDict


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


def mut_toposort(data: ta.Dict[T, ta.Set[T]]) -> ta.Iterator[ta.Set[T]]:
    for k, v in data.items():
        v.discard(k)
    extra_items_in_deps = functools.reduce(set.union, data.values()) - set(data.keys())
    data.update({item: set() for item in extra_items_in_deps})
    while True:
        ordered = set(item for item, dep in data.items() if not dep)
        if not ordered:
            break
        yield ordered
        data = {item: (dep - ordered) for item, dep in data.items() if item not in ordered}
    if data:
        raise ValueError('Cyclic dependencies exist among these items: ' + ' '.join(repr(x) for x in data.items()))


def toposort(data: ta.Mapping[T, ta.AbstractSet[T]]) -> ta.Iterator[ta.Set[T]]:
    return mut_toposort({k: set(v) for k, v in data.items()})


def partition(items: ta.Iterable[T], pred: ta.Callable[[T], bool]) -> ta.Tuple[ta.List[T], ta.List[T]]:
    t: ta.List[T] = []
    f: ta.List[T] = []
    for e in items:
        if pred(e):
            t.append(e)
        else:
            f.append(e)
    return t, f


def unique(it: ta.Iterable[T]) -> ta.List[T]:
    if isinstance(it, str):
        raise TypeError(it)
    ret: ta.List[T] = []
    seen: ta.Set[T] = set()
    for e in it:
        if e not in seen:
            seen.add(e)
            ret.append(e)
    return ret


def unique_dict(items: ta.Iterable[ta.Tuple[K, V]], *, identity: bool = False) -> ta.Dict[K, V]:
    dct = IdentityKeyDict() if identity else {}
    for k, v in items:
        if k in dct:
            raise KeyError(k)
        dct[k] = v
    return dct


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
