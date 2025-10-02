import collections.abc
import dataclasses as dc
import typing as ta

from ... import check
from ... import reflect as rfl
from ..base.contexts import MarshalContext
from ..base.contexts import MarshalFactoryContext
from ..base.contexts import UnmarshalContext
from ..base.contexts import UnmarshalFactoryContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value
from ..factories.method import MarshalerFactoryMethodClass
from ..factories.method import UnmarshalerFactoryMethodClass


##


DEFAULT_MAPPING_CONCRETE_TYPES: dict[type[collections.abc.Mapping], type[collections.abc.Mapping]] = {
    collections.abc.Mapping: dict,  # type: ignore
    collections.abc.MutableMapping: dict,  # type: ignore
}


#


@dc.dataclass(frozen=True)
class MappingMarshaler(Marshaler):
    ke: Marshaler
    ve: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Mapping) -> Value:
        return {
            self.ke.marshal(ctx, uk): self.ve.marshal(ctx, uv)
            for uk, uv in check.isinstance(o, collections.abc.Mapping).items()
        }


class MappingMarshalerFactory(MarshalerFactoryMethodClass):
    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_generic(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Mapping)):
            return None
        kt, vt = rty.args
        return lambda: MappingMarshaler(ctx.make_marshaler(kt), ctx.make_marshaler(vt))

    @MarshalerFactoryMethodClass.make_marshaler.register
    def _make_concrete(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, collections.abc.Mapping)):
            return None
        return lambda: MappingMarshaler(a := ctx.make_marshaler(ta.Any), a)


#


@dc.dataclass(frozen=True)
class MappingUnmarshaler(Unmarshaler):
    ctor: ta.Callable[[ta.Mapping[ta.Any, ta.Any]], ta.Mapping]
    ke: Unmarshaler
    ve: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Mapping:
        dct: dict = {}
        for mk, mv in check.isinstance(v, collections.abc.Mapping).items():
            dct[self.ke.unmarshal(ctx, mk)] = self.ve.unmarshal(ctx, mv)
        return self.ctor(dct)


class MappingUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_generic(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Mapping)):
            return None
        cty = DEFAULT_MAPPING_CONCRETE_TYPES.get(rty.cls, rty.cls)  # noqa
        kt, vt = rty.args
        return lambda: MappingUnmarshaler(cty, ctx.make_unmarshaler(kt), ctx.make_unmarshaler(vt))

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_concrete(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, collections.abc.Mapping)):
            return None
        return lambda: MappingUnmarshaler(check.isinstance(rty, type), a := ctx.make_unmarshaler(ta.Any), a)
