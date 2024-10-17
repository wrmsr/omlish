import typing as ta

from ... import lang
from .base import Builder
from .base import Node


##


class Ident(Node, lang.Final):
    s: str


CanIdent: ta.TypeAlias = Ident | str


class IdentBuilder(Builder):
    def ident(self, o: CanIdent) -> Ident:
        if isinstance(o, Ident):
            return o
        elif isinstance(o, str):
            return Ident(o)
        else:
            raise TypeError(o)

    @ta.final
    def i(self, o: CanIdent) -> Ident:
        return self.ident(o)
