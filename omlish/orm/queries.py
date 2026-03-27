import typing as ta

from .. import lang


T = ta.TypeVar('T')


##


@ta.final
class Query(lang.Final, ta.Generic[T]):
    def __init__(
            self,
            cls: type[T],
            where: ta.Mapping[str, ta.Any],
    ) -> None:
        super().__init__()

        self._cls = cls
        self._where = where

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._cls!r}, {self._where!r})'

    @property
    def cls(self) -> type[T]:
        return self._cls

    @property
    def where(self) -> ta.Mapping[str, ta.Any]:
        return self._where
