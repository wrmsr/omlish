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


def _get_maybe_element(rty: rfl.Type) -> rfl.Type | None:
    if not (isinstance(rty, rfl.Instance) and rty.type.runtime_object is lang.Maybe and len(rty.args) == 1):
        return None
    return check.single(rty.args)


def _get_maybe_cls(rty: rfl.Type) -> type | None:
    if not isinstance(rty, rfl.Instance):
        return None
    if (cls := rfl.get_runtime_type_or_none(rty)) is None or not issubclass(cls, lang.Maybe):
        return None
    return cls


class MaybeMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_generic(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (ety := _get_maybe_element(rty)) is None:
            return None
        return lambda: MaybeMarshaler(ctx.make_marshaler(ety))

    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_concrete(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if _get_maybe_cls(rty) is None:
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
        if (ety := _get_maybe_element(rty)) is None:
            return None
        return lambda: MaybeUnmarshaler(ctx.make_unmarshaler(ety))

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_concrete(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if _get_maybe_cls(rty) is None:
            return None
        return lambda: MaybeUnmarshaler(ctx.make_unmarshaler(ta.Any))
