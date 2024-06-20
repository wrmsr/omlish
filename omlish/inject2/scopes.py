from .. import dataclasses as dc
from .. import lang
from .elements import Element
from .keys import Key


class Scope(lang.Abstract):
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
