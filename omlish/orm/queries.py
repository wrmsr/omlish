import typing as ta

from .. import lang
from .ordering import Ordering


T = ta.TypeVar('T')


##


@ta.final
class Query(lang.Final, ta.Generic[T]):
    def __init__(
            self,
            cls: type[T],
            where: ta.Mapping[str, ta.Any] | None = None,
            /,
            order_by: Ordering | None = None,
    ) -> None:
        super().__init__()

        self._cls = cls
        self._where = where
        self._order_by = order_by

    def __repr__(self) -> str:
        return ''.join([
            f'{self.__class__.__name__}(',
            ', '.join([
                f'{self._cls!r}',
                *([f'{self._where!r}'] if self._where else []),
                *([f'order_by={self._order_by!r}'] if self._order_by else []),
            ]),
            f')',
        ])

    @property
    def cls(self) -> type[T]:
        return self._cls

    @property
    def where(self) -> ta.Mapping[str, ta.Any] | None:
        return self._where

    @property
    def order_by(self) -> Ordering | None:
        return self._order_by
