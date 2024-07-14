import typing as ta

from .. import lang


T = ta.TypeVar('T')
FT = ta.TypeVar('FT')
TT = ta.TypeVar('TT')

WrapperManagedIteratorT = ta.TypeVar('WrapperManagedIteratorT', bound='WrapperManagedIterator')


class ManagedIterator(lang.Abstract, lang.ContextManaged, ta.Iterator[T]):
    pass


class WrapperManagedIterator(ManagedIterator[T]):

    def __init__(self, wrapped: ManagedIterator[T]) -> None:
        super().__init__()

        self._wrapped = self.__wrapped__ = wrapped

    def __enter__(self: WrapperManagedIteratorT) -> WrapperManagedIteratorT:
        self._wrapped.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._wrapped.__exit__(exc_type, exc_val, exc_tb)

    def __next__(self) -> T:
        return self._wrapped.__next__()


class TransformedManagedIterator(WrapperManagedIterator[TT], ta.Generic[FT, TT]):

    _wrapped: ManagedIterator[FT]

    def __init__(self, transform: ta.Callable[[ta.Iterable[FT]], ta.Iterable[TT]], wrapped: ManagedIterator[FT]) -> None:  # noqa
        super().__init__(wrapped)

        self._transform = transform

        self._transformed_iter: ta.Optional[ta.Iterator[TT]] = None

    def __next__(self) -> T:
        if self._transformed_iter is None:
            self._transformed_iter = iter(self._transform(self._wrapped))
            self.__next__ = self._transformed_iter.__next__
        return self._transformed_iter.__next__()
