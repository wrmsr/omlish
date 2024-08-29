import collections.abc
import dataclasses as dc
import typing as ta

from .. import check
from .. import matchfns as mfs
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactoryMatchClass
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactoryMatchClass
from .values import Value


DEFAULT_MAPPING_CONCRETE_TYPES: dict[type[collections.abc.Mapping], type[collections.abc.Mapping]] = {
    collections.abc.Mapping: dict,  # type: ignore
    collections.abc.MutableMapping: dict,  # type: ignore
}


@dc.dataclass(frozen=True)
class MappingMarshaler(Marshaler):
    ke: Marshaler
    ve: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Mapping) -> Value:
        return {
            self.ke.marshal(ctx, uk): self.ve.marshal(ctx, uv)
            for uk, uv in check.isinstance(o, collections.abc.Mapping).items()
        }


class MappingMarshalerFactory(MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Mapping))
    def _build_generic(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        gty = check.isinstance(rty, rfl.Generic)
        kt, vt = gty.args
        return MappingMarshaler(ctx.make(kt), ctx.make(vt))

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, collections.abc.Mapping))
    def _build_concrete(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        return MappingMarshaler(a := ctx.make(ta.Any), a)


@dc.dataclass(frozen=True)
class MappingUnmarshaler(Unmarshaler):
    ctor: ta.Callable[[ta.Mapping[ta.Any, ta.Any]], ta.Mapping]
    ke: Unmarshaler
    ve: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Mapping:
        dct: dict = {}
        for mk, mv in check.isinstance(v, collections.abc.Mapping).items():
            dct[self.ke.unmarshal(ctx, mk)] = self.ve.unmarshal(ctx, mv)  # type: ignore
        return self.ctor(dct)


class MappingUnmarshalerFactory(UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Mapping))
    def _build_generic(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        gty = check.isinstance(rty, rfl.Generic)
        cty = DEFAULT_MAPPING_CONCRETE_TYPES.get(gty.cls, gty.cls)  # noqa
        kt, vt = gty.args
        return MappingUnmarshaler(cty, ctx.make(kt), ctx.make(vt))

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, collections.abc.Mapping))
    def _build_concrete(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler:
        return MappingUnmarshaler(check.isinstance(rty, type), a := ctx.make(ta.Any), a)
