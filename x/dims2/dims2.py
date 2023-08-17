import typing as ta

from omlish import lang


class Sym:
    pass


SymInt: ta.TypeAlias = ta.Union[Sym, int]


SymIntT = ta.TypeVar('SymIntT', bound=SymInt)


class BaseDims(tuple[SymIntT], lang.Abstract, ta.Generic[SymIntT]):
    pass


class BaseShape(BaseDims[SymIntT], lang.Abstract, ta.Generic[SymIntT]):
    pass


class Shape(BaseShape[SymInt], lang.Final):
    pass


class IntShape(BaseShape[int], lang.Final):
    pass


class BaseStrides(BaseDims[SymIntT], lang.Abstract, ta.Generic[SymIntT]):
    pass


class Strides(BaseStrides[SymInt], lang.Final):
    pass


class IntStrides()


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
