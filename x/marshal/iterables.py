import dataclasses as dc
import functools
import typing as ta

from omlish import check

from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .specs import Generic
from .specs import Spec
from .values import Value


@dc.dataclass(frozen=True)
class IterableMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Iterable) -> Value:
        return list(map(functools.partial(self.e.marshal, ctx), o))


class IterableMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, spec: Spec) -> ta.Optional[Marshaler]:
        if isinstance(spec, Generic) and spec.cls is list:
            if (e := ctx.make(check.single(spec.args))) is None:
                return None
            return IterableMarshaler(e)
        return None
