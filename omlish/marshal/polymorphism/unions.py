import typing as ta

from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import MarshalerFactory
from ..base.types import Unmarshaler
from ..base.types import UnmarshalerFactory
from .marshal import make_polymorphism_marshaler
from .metadata import Impls
from .metadata import TypeTagging
from .metadata import WrapperTypeTagging
from .unmarshal import make_polymorphism_unmarshaler


##


@dc.dataclass(frozen=True)
class _BasePolymorphismUnionFactory(lang.Abstract):
    impls: Impls
    tt: TypeTagging = WrapperTypeTagging()
    allow_partial: bool = dc.field(default=False, kw_only=True)

    @cached.property
    @dc.init
    def rtys(self) -> frozenset[rfl.Type]:
        return frozenset(i.ty for i in self.impls)

    def _guard(self, rty: rfl.Type) -> bool:
        if not isinstance(rty, rfl.Union):
            return False
        if self.allow_partial:
            return not (rty.args - self.rtys)
        else:
            return rty.args == self.rtys

    def get_impls(self, rty: rfl.Type) -> Impls:
        uty = check.isinstance(rty, rfl.Union)
        return Impls([self.impls.by_ty[check.isinstance(a, type)] for a in uty.args])


@dc.dataclass(frozen=True)
class PolymorphismUnionMarshalerFactory(_BasePolymorphismUnionFactory, MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not self._guard(rty):
            return None
        return lambda: make_polymorphism_marshaler(self.get_impls(rty), self.tt, ctx)


@dc.dataclass(frozen=True)
class PolymorphismUnionUnmarshalerFactory(_BasePolymorphismUnionFactory, UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not self._guard(rty):
            return None
        return lambda: make_polymorphism_unmarshaler(self.get_impls(rty), self.tt, ctx)
