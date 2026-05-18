"""
TODO:
 - unions / bases
  - prob just 'sharing' / 'inheriting'?
   - well, prob better to have fat registration than polling multiple cfg changes every time
 - configurable deser behavior - UnknownImpl vs raise
 - manifest interop
"""
import abc
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..api.configs import ConfigRegistry
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.internalstate import InternalState
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.values import Value
from .api import Impls
from .api import OpenPolymorphismImpl
from .api import PolymorphismOptions
from .api import polymorphism_from_impls
from .marshal import make_polymorphism_marshaler
from .unmarshal import make_polymorphism_unmarshaler


HandlerContextT = ta.TypeVar('HandlerContextT', bound=MarshalContext | UnmarshalContext)
HandlerT = ta.TypeVar('HandlerT', bound=Marshaler | Unmarshaler)


##


class _OpenPolymorphismBase(lang.Abstract, ta.Generic[HandlerContextT, HandlerT]):
    def __init__(
            self,
            ty: type,
            opts: PolymorphismOptions = PolymorphismOptions(),
    ) -> None:
        super().__init__()

        self._ty = ty
        self._opts = opts

    class _StateTup(ta.NamedTuple):
        config_impls: ta.Any
        impls: Impls
        handler: ta.Any

    @dc.dataclass()
    class _State(InternalState.ByConfig.ByHandler.Entry):
        tup: _OpenPolymorphismBase._StateTup | None = None

    def _get_handler(self, ctx: HandlerContextT) -> HandlerT:
        cr = check.isinstance(ctx.configs, ConfigRegistry)

        sbh: InternalState.ByConfig.ByHandler = ctx.internal_state_by_config.by_handler(self)  # type: ignore[arg-type]
        stx = sbh.get(_OpenPolymorphismBase._State)
        st = stx.tup

        config_impls: ta.Any = cr.get(self._ty).get(OpenPolymorphismImpl)
        if st is not None and config_impls is not None and st.config_impls is config_impls:
            return st.handler

        impls = polymorphism_from_impls(
            self._ty,
            [ic.impl_ty for ic in config_impls],
            naming=self._opts.naming,
            strip_suffix=self._opts.strip_suffix,
        ).impls

        h = self._make_handler(ctx, impls)

        st = self._StateTup(
            config_impls,
            impls,
            h,
        )

        stx.tup = st
        return h

    @abc.abstractmethod
    def _make_handler(
            self,
            ctx: HandlerContextT,
            impls: Impls,
    ) -> HandlerT:
        raise NotImplementedError


class OpenPolymorphismMarshaler(_OpenPolymorphismBase[MarshalContext, Marshaler], Marshaler):
    def _make_handler(
            self,
            ctx: MarshalContext,
            impls: Impls,
    ) -> Marshaler:
        return make_polymorphism_marshaler(
            impls,
            self._opts.type_tagging,
            ctx.marshal_factory_context,
        )

    def marshal(self, ctx: MarshalContext, o: ta.Any | None) -> Value:
        return self._get_handler(ctx).marshal(ctx, o)


class OpenPolymorphismUnmarshaler(_OpenPolymorphismBase[UnmarshalContext, Unmarshaler], Unmarshaler):
    def _make_handler(
            self,
            ctx: UnmarshalContext,
            impls: Impls,
    ) -> Unmarshaler:
        return make_polymorphism_unmarshaler(
            impls,
            self._opts.type_tagging,
            ctx.unmarshal_factory_context,
        )

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any | None:
        return self._get_handler(ctx).unmarshal(ctx, v)


##


@dc.dataclass(frozen=True)
class OpenPolymorphismMarshalerFactory(MarshalerFactory):
    ty: type
    opts: PolymorphismOptions = PolymorphismOptions()

    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if rty != self.ty:
            return None
        return lambda: OpenPolymorphismMarshaler(self.ty, self.opts)


@dc.dataclass(frozen=True)
class OpenPolymorphismUnmarshalerFactory(UnmarshalerFactory):
    ty: type
    opts: PolymorphismOptions = PolymorphismOptions()

    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if rty != self.ty:
            return None
        return lambda: OpenPolymorphismUnmarshaler(self.ty, self.opts)
