import typing as ta

from .. import check
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


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ScopeSeed(Element, lang.Final):
    key: Key


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class SeededScope(Scope, lang.Final):
    tag: ta.Any = dc.field(validate=check.not_none)
