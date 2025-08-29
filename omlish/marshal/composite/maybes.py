"""
TODO:
 - option to coordinate with objects and omit if empty / render unboxed
"""
import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value
from ..factories.match import MarshalerFactoryMatchClass
from ..factories.match import UnmarshalerFactoryMatchClass


##


@dc.dataclass(frozen=True)
class MaybeMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        m: lang.Maybe = o
        if m.present:
            return [self.e.marshal(ctx, m.must())]
        else:
            return []


class MaybeMarshalerFactory(MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is lang.Maybe)
    def _build_generic(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        gty = check.isinstance(rty, rfl.Generic)
        return MaybeMarshaler(ctx.make(check.single(gty.args)))

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, lang.Maybe))
    def _build_concrete(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return MaybeMarshaler(ctx.make(ta.Any))


@dc.dataclass(frozen=True)
class MaybeUnmarshaler(Unmarshaler):
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        if v:
            return lang.just(self.e.unmarshal(ctx, check.single(v)))  # type: ignore
        else:
            return lang.empty()


class MaybeUnmarshalerFactory(UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and rty.cls is lang.Maybe)
    def _build_generic(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        gty = check.isinstance(rty, rfl.Generic)
        return MaybeUnmarshaler(ctx.make(check.single(gty.args)))

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, lang.Maybe))
    def _build_concrete(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return MaybeUnmarshaler(ctx.make(ta.Any))
