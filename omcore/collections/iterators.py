import typing as ta


T = ta.TypeVar('T')


##


class HasNextIterator(ta.Protocol[T]):
    def __iter__(self) -> HasNextIterator[T]: ...

    def __next__(self) -> T: ...

    def has_next(self) -> bool: ...
