import typing as ta

from ... import dataclasses as dc
from ... import lang
from .base import Builder


##


@dc.dataclass(frozen=True)
class Param(lang.Final):
    n: str | None = None

    def __repr__(self) -> str:
        if self.n is not None:
            return f'{self.__class__.__name__}({self.n!r})'
        else:
            return f'{self.__class__.__name__}(@{hex(id(self))[2:]})'

    def __eq__(self, other):
        if not isinstance(other, Param):
            return False
        if self.n is None and other.n is None:
            return self is other
        else:
            return self.n == other.n


##


CanParam: ta.TypeAlias = Param | str | None


def as_param(o: CanParam = None) -> Param:
    if isinstance(o, Param):
        return o
    else:
        return Param(o)


##


class ParamAccessor(lang.Final):
    def __getattr__(self, s: str) -> Param:
        return Param(s)

    def __call__(self, o: CanParam = None) -> Param:
        return as_param(o)


##


class ParamBuilder(Builder):
    @ta.final
    def param(self, o: CanParam = None) -> Param:
        return as_param(o)

    @ta.final
    @property
    def p(self) -> ParamAccessor:
        return ParamAccessor()
