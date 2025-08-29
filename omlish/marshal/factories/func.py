import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..base.contexts import MarshalContext
from ..base.contexts import UnmarshalContext
from ..base.types import Marshaler
from ..base.types import Unmarshaler
from ..base.values import Value


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
