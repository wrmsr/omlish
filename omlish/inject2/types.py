import typing as ta

from .. import lang


##


Cls = type | ta.NewType


##


class Scope(lang.Abstract):
    def __repr__(self) -> str:
        return type(self).__name__


class Unscoped(Scope, lang.Singleton, lang.Final):
    pass
