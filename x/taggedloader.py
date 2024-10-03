import dataclasses as dc
import typing as ta

from omlish import lang


T = ta.TypeVar('T')
V = ta.TypeVar('V')


##


@dc.dataclass(frozen=True)
class TaggedValue(lang.Final, ta.Generic[T, V]):
    t: T
    v: V


##


@dc.dataclass(frozen=True)
class Location(lang.Final):
    l: int
    c: int
    b: int


##


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
