import typing as ta

from ... import dataclasses as dc
from ..api.contexts import MarshalContext
from ..api.contexts import UnmarshalContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value


##


@dc.dataclass(frozen=True)
class ConstMarshaler(Marshaler):
    v: Value

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self.v


@dc.dataclass(frozen=True)
class ConstUnmarshaler(Unmarshaler):
    o: ta.Any

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.o
