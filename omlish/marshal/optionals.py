import dataclasses as dc
import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
from .specs import Spec
from .specs import Union
from .values import Value


@dc.dataclass(frozen=True)
class OptionalMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Optional[ta.Any]) -> Value:
        if o is None:
            return None
        return self.e.marshal(ctx, o)


class OptionalMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if isinstance(spec, Union) and spec.is_optional:  # type: ignore
            if (e := ctx.make(spec.without_none())) is None:
                return None  # type: ignore
            return OptionalMarshaler(e)
        return None


@dc.dataclass(frozen=True)
class OptionalUnmarshaler(Unmarshaler):
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Optional[ta.Any]:
        if v is None:
            return None
        return self.e.unmarshal(ctx, v)


class OptionalUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, spec: Spec) -> ta.Optional[Unmarshaler]:
        if isinstance(spec, Union) and spec.is_optional:  # type: ignore
            if (e := ctx.make(spec.without_none())) is None:
                return None  # type: ignore
            return OptionalUnmarshaler(e)
        return None
