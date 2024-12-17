import abc
import functools
import typing as ta

from ... import lang
from .base import Builder
from .base import Node


##


class IdentLike(abc.ABC):  # noqa
    pass


##


class Ident(Node, IdentLike, lang.Final):
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


CanIdent: ta.TypeAlias = IdentLike | Ident | str


class IdentAccessor(lang.Final):
    def __getattr__(self, s: str) -> Ident:
        return Ident(s)

    def __call__(self, o: CanIdent) -> Ident:
        return as_ident(o)


##


class IdentBuilder(Builder):
    @ta.final
    def ident(self, o: CanIdent) -> Ident:
        return as_ident(o)

    @ta.final
    @property
    def i(self) -> IdentAccessor:
        return IdentAccessor()
