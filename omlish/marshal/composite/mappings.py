import collections.abc
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import reflect as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.options import Options
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value
from ..factories.method import MarshalerFactoryMethodClass
from ..factories.method import UnmarshalerFactoryMethodClass
from .api import DefaultMappingConstructors


##


DEFAULT_MAPPING_CONCRETE_TYPES: dict[type[collections.abc.Mapping], type[collections.abc.Mapping]] = {
    collections.abc.Mapping: dict,  # type: ignore
    collections.abc.MutableMapping: dict,  # type: ignore
}


def get_default_mapping_constructor(
        cls: type,
        options: Options | None = None,
) -> ta.Callable[[collections.abc.Mapping], ta.Any]:
    if options is not None and (opt := options.get(DefaultMappingConstructors)) is not None:
        opt = check.isinstance(opt, DefaultMappingConstructors)
        o_ctor: ta.Any = None
        if cls == collections.abc.Mapping:
            o_ctor = opt.mapping
        elif cls == collections.abc.MutableMapping:
            o_ctor = opt.mutable_mapping
        if o_ctor is not None:
            return o_ctor

    return DEFAULT_MAPPING_CONCRETE_TYPES.get(cls, cls)  # noqa


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
    cls: type
    ke: Unmarshaler
    ve: Unmarshaler

    ctor: ta.Callable[[ta.Mapping[ta.Any, ta.Any]], ta.Mapping] | None = None

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Mapping:
        dct: dict = {}
        for mk, mv in check.isinstance(v, collections.abc.Mapping).items():
            dct[self.ke.unmarshal(ctx, mk)] = self.ve.unmarshal(ctx, mv)
        if (ctor := self.ctor) is None:
            ctor = get_default_mapping_constructor(self.cls, ctx.options)
        if ctor is dict:
            return dct
        return ctor(dct)


class MappingUnmarshalerFactory(UnmarshalerFactoryMethodClass):
    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_generic(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Mapping)):
            return None
        kt, vt = rty.args
        return lambda: MappingUnmarshaler(rty.cls, ctx.make_unmarshaler(kt), ctx.make_unmarshaler(vt))  # noqa

    @UnmarshalerFactoryMethodClass.make_unmarshaler.register
    def _make_concrete(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (isinstance(rty, type) and issubclass(rty, collections.abc.Mapping)):
            return None
        return lambda: MappingUnmarshaler(check.isinstance(rty, type), a := ctx.make_unmarshaler(ta.Any), a)
