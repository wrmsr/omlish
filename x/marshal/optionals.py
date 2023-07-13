import dataclasses as dc
import typing as ta

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .specs import Spec
from .specs import Union
from .values import Value


@dc.dataclass(frozen=True)
class OptionalMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        if o is None:
            return None
        return self.e.marshal(ctx, o)


class OptionalMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if isinstance(spec, Union) and spec.is_optional:
            if (e := ctx.make(spec.without_none())) is None:
                return None
            return OptionalMarshaler(e)
        return None
