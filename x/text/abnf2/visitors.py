import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dispatch
from omlish import lang

from .base import Match
from .base import Parser
from .parsers import RuleRef


T = ta.TypeVar('T')


##


class ParserVisitor(lang.Abstract, ta.Generic[T]):
    @dispatch.method()
    def visit_parser(self, p: Parser, m: Match) -> T:
        raise TypeError(p)

    #

    def visit_match(self, m: Match) -> T:
        return self.visit_parser(m.parser, m)


##


class RuleVisitor(lang.Abstract, ta.Generic[T]):
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
        return self.visit_rule(check.isinstance(m.parser, RuleRef).name, m)
