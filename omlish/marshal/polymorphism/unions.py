import typing as ta

from .. import Polymorphism
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
from .types import Impls
from .types import TypeTagging
from .types import WrapperTypeTagging
from .unmarshal import make_polymorphism_unmarshaler


##


@dc.dataclass(frozen=True)
class _BasePolymorphismUnionFactory(lang.Abstract):
    p: Polymorphism
    tt: TypeTagging = WrapperTypeTagging()
    allow_partial: bool = dc.field(default=False, kw_only=True)

    @cached.property
    @dc.init
    def rtys(self) -> frozenset[rfl.Type]:
        return frozenset(i.ty for i in self.p.impls)

    def get_impls(self, rty: rfl.Type) -> Impls | None:
        if not isinstance(rty, rfl.Union):
            return None
        elif self.allow_partial:
            if not (rty.args - self.rtys):
                return None
        else:
            if not rty.args != self.rtys:
                return None

        uty = check.isinstance(rty, rfl.Union)
        return Impls([self.p.impls.by_ty[check.isinstance(a, type)] for a in uty.args])


@dc.dataclass(frozen=True)
class PolymorphismUnionMarshalerFactory(_BasePolymorphismUnionFactory, MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (impls := self.get_impls(rty)) is None:
            return None
        return lambda: make_polymorphism_marshaler(impls, self.tt, ctx)


@dc.dataclass(frozen=True)
class PolymorphismUnionUnmarshalerFactory(_BasePolymorphismUnionFactory, UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (impls := self.get_impls(rty)) is None:
            return None
        return lambda: make_polymorphism_unmarshaler(impls, self.tt, ctx)
