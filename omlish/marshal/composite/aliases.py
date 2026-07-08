"""
These factories unwrap `type X = ...` aliases to their (argument-substituted) targets. Recursive aliases terminate
through the standard machinery: a recursive occurrence re-reflects to the same alias node, whose type key hits the type
cache, whose in-progress entry is knot-tied by the recursive proxy factory.
"""

import typing as ta

from ... import reflect2 as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory


##


class TypeAliasMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not isinstance(rty, rfl.TypeAliasType):
            return None
        tgt = rfl.get_type_alias_target(rty)
        return lambda: ctx.make_marshaler(tgt)


class TypeAliasUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not isinstance(rty, rfl.TypeAliasType):
            return None
        tgt = rfl.get_type_alias_target(rty)
        return lambda: ctx.make_unmarshaler(tgt)
