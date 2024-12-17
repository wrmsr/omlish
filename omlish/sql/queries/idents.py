import functools
import typing as ta

from ... import check
from ... import lang
from .base import Builder
from .base import Node


##


class Ident(Node, lang.Final):
    s: str


##


@functools.singledispatch
def as_ident(o: ta.Any) -> Ident:
    raise TypeError(o)


@as_ident.register
def _(i: Ident) -> Ident:
    return i


@as_ident.register
def _(s: str) -> Ident:
    return Ident(s)


##


class IdentAccessor:
    def __getattr__(self, s: str) -> Ident:
        check.not_in('.', s)
        check.arg(not s.startswith('__'))
        return Ident(s)


##


CanIdent: ta.TypeAlias = Ident | str


class IdentBuilder(Builder):
    def ident(self, o: CanIdent) -> Ident:
        return as_ident(o)

    @ta.final
    def i(self, o: CanIdent) -> Ident:
        return self.ident(o)
