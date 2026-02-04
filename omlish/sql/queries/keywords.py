import typing as ta

from ... import lang
from .base import Builder
from .base import Node


##


class Keyword(Node, lang.Abstract):
    pass


class LiteralKeyword(Keyword, lang.Final):
    s: str


class Star(Keyword, lang.Final):
    pass


CanKeyword: ta.TypeAlias = Keyword | str


class KeywordBuilder(Builder):
    def keyword(self, k: str) -> Keyword:
        if isinstance(k, Keyword):
            return k
        elif isinstance(k, str):
            return LiteralKeyword(k)
        else:
            raise TypeError(k)

    def k(self, k: CanKeyword) -> Keyword:
        return self.keyword(k)

    @property
    def star(self) -> Star:
        return Star()
