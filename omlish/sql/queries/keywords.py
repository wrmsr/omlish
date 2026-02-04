import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from .base import Builder
from .base import Node


##


class Keyword(Node, lang.Abstract):
    pass


class LiteralKeyword(Keyword, lang.Final):
    s: str = dc.xfield(coerce=check.non_empty_str)


class Star(Keyword, lang.Final):
    pass


##


CanKeyword: ta.TypeAlias = Keyword | str


class KeywordAccessor(lang.Final):
    def __getattr__(self, s: str) -> LiteralKeyword:
        return LiteralKeyword(s)

    def __call__(self, o: str) -> LiteralKeyword:
        return LiteralKeyword(o)


##


class KeywordBuilder(Builder):
    @ta.final
    def keyword(self, k: CanKeyword) -> Keyword:
        if isinstance(k, Keyword):
            return k
        elif isinstance(k, str):
            return LiteralKeyword(k)
        else:
            raise TypeError(k)

    @ta.final
    @property
    def k(self) -> KeywordAccessor:
        return KeywordAccessor()

    @ta.final
    @property
    def star(self) -> Star:
        return Star()
