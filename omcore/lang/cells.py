import abc
import types
import typing as ta

from ..lite.abstract import Abstract


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


class BaseCell(Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def __call__(self) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, v: T) -> None:
        raise NotImplementedError

    #

    @ta.final
    def __bool__(self):
        raise TypeError(self)

    @ta.final
    def __hash__(self):
        raise TypeError(self)

    @ta.final
    def __eq__(self, other):
        raise TypeError(self)

    @ta.final
    def __ne__(self, other):
        raise TypeError(self)


##


@ta.final
class _Cell(BaseCell):
    def __init__(self, v):
        self._v = v

    def __repr__(self):
        return f'_Cell({self._v!r})'

    def __call__(self):
        return self._v

    def set(self, v):
        self._v = v


def cell(v: T) -> Cell[T]:
    return _Cell(v)


#


@ta.final
class _CellCell(BaseCell):
    def __init__(self, c: types.CellType) -> None:
        self._c = c

    def __repr__(self):
        return f'_CellCell({self._c!r})'

    def __call__(self):
        return self._c.cell_contents

    def set(self, v):
        self._c.cell_contents = v


def cell_cell(c: types.CellType) -> Cell:
    return _CellCell(c)
