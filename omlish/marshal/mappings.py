import collections.abc
import dataclasses as dc
import functools
import typing as ta

from .. import check
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .values import Value


@dc.dataclass(frozen=True)
class MappingMarshaler(Marshaler):
    ke: Marshaler
    ve: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Mapping) -> Value:
        # return list(map(functools.partial(self.e.marshal, ctx), o))
        raise NotImplementedError


class MappingMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Optional[Marshaler]:
        if isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Mapping):
            kt, vt = rty.args
            if (ke := ctx.make(kt)) is None or (ve := ctx.make(vt)) is None:
                return None  # type: ignore
            return MappingMarshaler(ke, ve)
        if isinstance(rty, type) and issubclass(rty, collections.abc.Mapping):
            if (e := ctx.make(ta.Any)) is None:
                return None  # type: ignore
            return MappingMarshaler(e, e)
        return None


@dc.dataclass(frozen=True)
class MappingUnmarshaler(Unmarshaler):
    ctor: ta.Callable[[ta.Mapping[ta.Any, ta.Any]], ta.Mapping]
    ke: Unmarshaler
    ve: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Mapping:
        # return self.ctor(map(functools.partial(self.e.unmarshal, ctx), check.isinstance(v, collections.abc.Mapping)))
        raise NotImplementedError


class MappingUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Optional[Unmarshaler]:
        if isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Mapping):
            kt, vt = rty.args
            if (ke := ctx.make(kt)) is None or (ve := ctx.make(vt)) is None:
                return None  # type: ignore
            return MappingUnmarshaler(rty.cls, ke, ve)
        if isinstance(rty, type) and issubclass(rty, collections.abc.Mapping):
            if (e := ctx.make(ta.Any)) is None:
                return None  # type: ignore
            return MappingUnmarshaler(rty, e, e)
        return None
