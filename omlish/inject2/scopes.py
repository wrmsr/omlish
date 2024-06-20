from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .keys import Key


class Scope(lang.Abstract):
    def __repr__(self) -> str:
        return type(self).__name__


class Unscoped(Scope, lang.Singleton, lang.Final):
    pass


class Singleton(Scope, lang.Singleton, lang.Final):
    pass


class Thread(Scope, lang.Singleton, lang.Final):
    pass


class SeededScope(Scope, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class ScopeSeed(Element, lang.Final):
    key: Key
