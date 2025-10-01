from ... import cached
from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..factories.simple import SimpleMarshalerFactory
from ..factories.simple import SimpleUnmarshalerFactory
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

    def guard(self, ctx: MarshalContext | UnmarshalContext, rty: rfl.Type) -> bool:
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
class PolymorphismUnionMarshalerFactory(_BasePolymorphismUnionFactory, SimpleMarshalerFactory):
    def fn(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return make_polymorphism_marshaler(self.get_impls(rty), self.tt, ctx)


@dc.dataclass(frozen=True)
class PolymorphismUnionUnmarshalerFactory(_BasePolymorphismUnionFactory, SimpleUnmarshalerFactory):
    def fn(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return make_polymorphism_unmarshaler(self.get_impls(rty), self.tt, ctx)
