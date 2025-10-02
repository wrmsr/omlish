import dataclasses as dc
import typing as ta

from ... import lang
from ... import reflect as rfl
from ...funcs import guard as gfs
from .contexts import MarshalContext
from .contexts import UnmarshalContext
from .types import Marshaler
from .types import MarshalerFactory
from .types import MarshalerMaker
from .types import Unmarshaler
from .types import UnmarshalerFactory
from .types import UnmarshalerMaker
from .values import Value


##


@dc.dataclass(frozen=True)
class FuncMarshaler(Marshaler, lang.Final):
    fn: ta.Callable[[MarshalContext, ta.Any], Value]

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self.fn(ctx, o)


@dc.dataclass(frozen=True)
class FuncUnmarshaler(Unmarshaler, lang.Final):
    fn: ta.Callable[[UnmarshalContext, Value], ta.Any]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.fn(ctx, v)


##


@dc.dataclass(frozen=True)
class FuncMarshalerFactory(MarshalerFactory):  # noqa
    gf: MarshalerMaker

    def make_marshaler(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        return self.gf(ctx, rty)


@dc.dataclass(frozen=True)
class FuncUnmarshalerFactory(UnmarshalerFactory):  # noqa
    gf: UnmarshalerMaker

    def make_unmarshaler(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        return self.gf(ctx, rty)


##


class GuardMethodMarshalerFactory(MarshalerFactory):
    @gfs.method(instance_cache=True)
    def make_marshaler(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        raise NotImplementedError
