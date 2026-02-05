"""
TODO:
 - option to coordinate with objects and omit if empty / render unboxed
"""
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value
from ..factories.method import MarshalerFactoryMethodClass
from ..factories.method import UnmarshalerFactoryMethodClass


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


class MaybeMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_generic(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, rfl.Generic) and rty.cls is lang.Maybe):
            return None
        return lambda: MaybeMarshaler(ctx.make_marshaler(check.single(rty.args)))

    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_concrete(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, lang.Maybe)):
            return None
        return lambda: MaybeMarshaler(ctx.make_marshaler(ta.Any))


#


@dc.dataclass(frozen=True)
class MaybeUnmarshaler(Unmarshaler):
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        if v:
            return lang.just(self.e.unmarshal(ctx, check.single(v)))  # type: ignore
        else:
            return lang.empty()


class MaybeUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_generic(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Generic) and rty.cls is lang.Maybe):
            return None
        return lambda: MaybeUnmarshaler(ctx.make_unmarshaler(check.single(rty.args)))

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_concrete(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, lang.Maybe)):
            return None
        return lambda: MaybeUnmarshaler(ctx.make_unmarshaler(ta.Any))
