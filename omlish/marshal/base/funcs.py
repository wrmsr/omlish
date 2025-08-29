import dataclasses as dc
import typing as ta

from ... import lang
from ... import reflect as rfl
from ...funcs import match as mfs
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
    guard: ta.Callable[[MarshalContext, rfl.Type], bool]
    fn: ta.Callable[[MarshalContext, rfl.Type], Marshaler]

    @lang.cached_property
    def make_marshaler(self) -> MarshalerMaker:
        return mfs.simple(self.guard, self.fn)


@dc.dataclass(frozen=True)
class FuncUnmarshalerFactory(UnmarshalerFactory):  # noqa
    guard: ta.Callable[[UnmarshalContext, rfl.Type], bool]
    fn: ta.Callable[[UnmarshalContext, rfl.Type], Unmarshaler]

    @lang.cached_property
    def make_unmarshaler(self) -> UnmarshalerMaker:
        return mfs.simple(self.guard, self.fn)
