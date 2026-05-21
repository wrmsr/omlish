# ruff: noqa: ANN204 PLW1641
"""
TODO:
 - SequenceLike / SequenceMixins
 - rename to typing or smth? it's kinda both

====

https://docs.python.org/3/library/collections.abc.html
https://github.com/python/cpython/blob/main/Doc/library/collections.abc.rst

https://github.com/python/mypy/blob/master/mypy/typeshed/stdlib/typing.pyi

https://github.com/python/typeshed/blob/main/stdlib/_collections_abc.pyi
https://github.com/python/mypy/blob/master/mypy/typeshed/stdlib/_collections_abc.pyi

====

Present in collections.abc but absent in docs:
- Set.__rand__
- Set.__ror__
- MutableSet.clear

Present in docs but absent in collections.abc:
- Mapping.__ne__
"""
import typing as ta


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')

T_co = ta.TypeVar('T_co', covariant=True)
K_co = ta.TypeVar('K_co', covariant=True)
V_co = ta.TypeVar('V_co', covariant=True)

T_contra = ta.TypeVar('T_contra', contravariant=True)


##


class Hashable(ta.Protocol):
    def __hash__(self) -> int: ...


class Iterable(ta.Protocol[T_co]):
    def __iter__(self) -> ta.Iterator[T_co]: ...


class Iterator(Iterable[T_co], ta.Protocol[T_co]):
    def __next__(self) -> T_co: ...

    # ::mixins::

    def __iter__(self) -> ta.Iterator[T_co]: ...


class Reversible(Iterable[T_co], ta.Protocol[T_co]):
    def __iter__(self) -> ta.Iterator[T_co]: ...

    def __reversed__(self) -> Iterator[T_co]: ...


class Sized(ta.Protocol):
    def __len__(self) -> int: ...


class Container(ta.Protocol[T_contra]):
    def __contains__(self, x: T_contra) -> bool: ...


class Collection(Sized, Iterable, Container, ta.Protocol):
    def __contains__(self, x): ...

    def __iter__(self): ...

    def __len__(self) -> int: ...


# region Sequence


class Sequence(Reversible, Collection, ta.Protocol):
    def __getitem__(self, index): ...

    def __len__(self) -> int: ...

    # ::mixins::

    def __contains__(self, x): ...

    def __iter__(self): ...

    def __reversed__(self): ...

    def index(self, value, start=0, stop=None): ...

    def count(self, value): ...


class MutableSequence(Sequence, ta.Protocol):
    def __getitem__(self, index): ...

    def __setitem__(self, index, value): ...

    def __delitem__(self, index): ...

    def __len__(self) -> int: ...

    def insert(self, index, value): ...

    # ::mixins::

    # Sequence

    def __contains__(self, x): ...

    def __iter__(self): ...

    def __reversed__(self): ...

    def index(self, value, start=0, stop=None): ...

    def count(self, value): ...

    # MutableSequence

    def append(self, value): ...

    def clear(self): ...

    def reverse(self): ...

    def extend(self, values): ...

    def pop(self, index=-1): ...

    def remove(self, value): ...

    def __iadd__(self, values): ...


# endregion


# region Set


class Set(Collection, ta.Protocol):
    def __contains__(self, item): ...

    def __iter__(self): ...

    def __len__(self) -> int: ...

    # ::mixins::

    def __le__(self, other): ...

    def __lt__(self, other): ...

    def __gt__(self, other): ...

    def __ge__(self, other): ...

    def __eq__(self, other): ...

    def __and__(self, other): ...

    def __rand__(self, other): ...

    def __or__(self, other): ...

    def __ror__(self, other): ...

    def __sub__(self, other): ...

    def __rsub__(self, other): ...

    def __xor__(self, other): ...

    def __rxor__(self, other): ...

    def isdisjoint(self, other): ...


class MutableSet(Set, ta.Protocol):
    def __contains__(self, item): ...

    def __iter__(self): ...

    def __len__(self) -> int: ...

    def add(self, value): ...

    def discard(self, value): ...

    # ::mixins::

    # Set

    def __le__(self, other): ...

    def __lt__(self, other): ...

    def __gt__(self, other): ...

    def __ge__(self, other): ...

    def __eq__(self, other): ...

    def __and__(self, other): ...

    def __rand__(self, other): ...

    def __or__(self, other): ...

    def __ror__(self, other): ...

    def __sub__(self, other): ...

    def __rsub__(self, other): ...

    def __xor__(self, other): ...

    def __rxor__(self, other): ...

    def isdisjoint(self, other): ...

    # MutableSet

    def remove(self, value): ...

    def pop(self): ...

    def clear(self): ...

    def __ior__(self, it): ...

    def __iand__(self, it): ...

    def __ixor__(self, it): ...

    def __isub__(self, it): ...


# endregion


# region Mapping


class Mapping(Collection, ta.Protocol):
    def __getitem__(self, key): ...

    def __iter__(self): ...

    def __len__(self) -> int: ...

    # ::mixins::

    def get(self, key, default=None): ...

    def keys(self): ...

    def items(self): ...

    def values(self): ...

    def __eq__(self, other): ...

    def __ne__(self, other): ...

    def __contains__(self, item): ...


class MutableMapping(Mapping, ta.Protocol):
    def __getitem__(self, key): ...

    def __setitem__(self, key, value): ...

    def __delitem__(self, key): ...

    def __iter__(self): ...

    def __len__(self) -> int: ...

    # ::mixins::

    # Mapping

    def get(self, key, default=None): ...

    def keys(self): ...

    def items(self): ...

    def values(self): ...

    def __eq__(self, other): ...

    def __ne__(self, other): ...

    def __contains__(self, item): ...

    # MutableMapping

    def pop(self, key, default=None): ...

    def popitem(self): ...

    def clear(self): ...

    def update(self, other=(), **kwds): ...

    def setdefault(self, key, default=None): ...


# endregion


# region Views


class MappingView(Sized, ta.Protocol):
    @property
    def _mapping(self): ...  # noqa

    # ::mixins::

    # __init__
    # __len__
    # __repr__


class KeysView(MappingView, Set, ta.Protocol):
    # ::mixins::

    # __contains__
    # __iter__

    pass


class ValuesView(MappingView, Collection, ta.Protocol):
    # ::mixins::

    # __contains__
    # __iter__

    pass


class ItemsView(MappingView, Set, ta.Protocol):
    # ::mixins::

    # __contains__
    # __iter__

    pass


# endregion
