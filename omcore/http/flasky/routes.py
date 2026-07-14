import typing as ta

from ... import cached
from ... import dataclasses as dc


##


class RouteKey(ta.NamedTuple):
    rule: str
    method: str


@dc.dataclass(frozen=True, kw_only=True)
class Route:
    rule: str
    endpoint: str
    methods: frozenset[str]

    @cached.property
    def keys(self) -> frozenset[RouteKey]:
        return frozenset(RouteKey(self.rule, m) for m in self.methods)
