import functools
import typing as ta


T = ta.TypeVar('T')


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
