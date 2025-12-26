import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dispatch
from omlish import lang

from .base import Match
from .base import Op
from .ops import RuleRef


T = ta.TypeVar('T')


##


class OpMatchVisitor(lang.Abstract, ta.Generic[T]):
    @dispatch.method()
    def visit_op(self, o: Op, m: Match) -> T:
        raise TypeError(o)

    #

    def visit_match(self, m: Match) -> T:
        return self.visit_op(m.op, m)


##


class RuleMatchVisitor(lang.Abstract, ta.Generic[T]):
    _registry = col.AttrRegistry[ta.Callable, str]()

    @classmethod
    def register(cls, name):
        return cls._registry.register(name)

    @lang.cached_function
    @classmethod
    def _registry_cache(cls) -> col.AttrRegistryCache[ta.Callable, str, ta.Mapping[str, str]]:
        def prepare(_, dct):
            return col.make_map(((n, a) for a, (_, n) in dct.items()), strict=True)

        return col.AttrRegistryCache(cls._registry, prepare)

    def visit_rule(self, name: str, m: Match) -> T:
        att = self._registry_cache().get(self.__class__)[name]
        return getattr(self, att)(m)

    #

    def visit_match(self, m: Match) -> T:
        return self.visit_rule(check.isinstance(m.op, RuleRef).name, m)
