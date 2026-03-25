import typing as ta


T = ta.TypeVar('T')


##


class Cell(ta.Protocol[T]):
    def __call__(self) -> T: ...

    def set(self, v: T) -> None: ...

    #

    def __bool__(self) -> ta.NoReturn: ...

    def __hash__(self) -> ta.NoReturn: ...

    def __eq__(self, other: object) -> ta.NoReturn: ...

    def __ne__(self, other: object) -> ta.NoReturn: ...


@ta.final
class _Cell:
    def __init__(self, v):
        self._v = v

    def __repr__(self):
        return f'_Cell({self._v!r})'

    def __call__(self):
        return self._v

    def set(self, v):
        self._v = v

    #

    def __bool__(self):
        raise TypeError(self)

    def __hash__(self):
        raise TypeError(self)

    def __eq__(self, other):
        raise TypeError(self)

    def __ne__(self, other):
        raise TypeError(self)


def cell(v: T) -> Cell[T]:
    return _Cell(v)
