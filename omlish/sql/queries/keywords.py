from ... import lang
from .base import Builder
from .base import Node


##


class Keyword(Node, lang.Abstract):
    pass


class Star(Keyword, lang.Final):
    pass


class KeywordBuilder(Builder):
    @property
    def star(self) -> Star:
        return Star()
