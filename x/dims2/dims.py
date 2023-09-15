"""
TODO:
 - __eq__ type constraining - ** strict_eq **
 - class Axes(Dims) ?
 - check non-neg, non-z?
"""
import typing as ta

from omlish import check
from omlish import dataclasses as dc


SelfT = ta.TypeVar('SelfT')
IntStrT = ta.TypeVar('IntStrT', bound=int | str)


class Dims(tuple[IntStrT]):
    def __new__(cls: ta.Type[SelfT], t: ta.Iterable[IntStrT]) -> SelfT:
        return super().__new__(cls, t)  # type: ignore


class Shape(Dims[IntStrT]):
    pass


class Stride(Dims[IntStrT]):
    pass


def _main() -> None:
    assert isinstance(Shape([1, 2, 3]), Shape)
    assert isinstance(Shape(['1', '2', '3']), Shape)
    assert isinstance(s := Shape(ta.cast(ta.List[int | str], ['1', 2, '3'])), Shape)
    if ta.TYPE_CHECKING:
        reveal_type(s)
    assert isinstance(Shape(['1', 2, 3.]), Shape)


if __name__ == '__main__':
    _main()
