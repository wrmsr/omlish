import typing as ta

from ... import dataclasses as dc
from ... import lang
from .base import Node
from .idents import CanIdent
from .idents import Ident
from .idents import IdentBuilder


##


class Name(Node, lang.Final):
    ps: ta.Sequence[Ident] = dc.xfield(coerce=tuple)


CanName: ta.TypeAlias = Name | CanIdent | ta.Sequence[CanIdent]


class NameBuilder(IdentBuilder):
    def name(self, o: CanName) -> Name:
        if isinstance(o, Name):
            return o
        elif isinstance(o, (Ident, str)):
            return Name([self.ident(o)])
        elif isinstance(o, ta.Sequence):
            return Name([self.ident(p) for p in o])
        else:
            raise TypeError(o)

    @ta.final
    def n(self, o: CanName) -> Name:
        return self.name(o)
