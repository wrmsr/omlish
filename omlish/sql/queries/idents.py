"""
TODO:
 - clamp down on as_ident / CanIdent - no strs allowed
"""
import abc
import functools
import typing as ta

from ... import cached
from ... import lang
from ..qualifiedname import QualifiedName
from .base import Builder
from .base import HasQn
from .base import Node


##


class IdentLike(abc.ABC):  # noqa
    pass


##


class Ident(Node, IdentLike, HasQn, lang.Final):
    s: str

    @cached.property
    def qn(self) -> QualifiedName:
        return QualifiedName((self.s,))


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
