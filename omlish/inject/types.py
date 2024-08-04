import typing as ta

from .. import lang


class Tag(ta.NamedTuple):
    tag: ta.Any


class Scope(lang.Abstract):
    def __repr__(self) -> str:
        return type(self).__name__


class Unscoped(Scope, lang.Singleton, lang.Final):
    pass
