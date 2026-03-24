import typing as ta


T = ta.TypeVar('T')

Comparer: ta.TypeAlias = ta.Callable[[T, T], int]


##


class TreapNode(ta.Protocol[T]):
    @property
    def value(self) -> T: ...

    @property
    def priority(self) -> int: ...

    @property
    def left(self) -> ta.Optional['TreapNode[T]']: ...

    @property
    def right(self) -> ta.Optional['TreapNode[T]']: ...

    @property
    def count(self) -> int: ...

    def __iter__(self) -> ta.Iterator[T]: ...


##


from ._treap_py import (  # noqa
    new,
    find,
    place,
    union,
    split,
    intersect,
    delete,
    diff,
)


try:
    from . import _treap  # type: ignore
except ImportError:
    pass
else:
    for a in [
        'new',
        'find',
        'place',
        'union',
        'split',
        'intersect',
        'delete',
        'diff',
    ]:
        globals()[a] = getattr(_treap, a)
