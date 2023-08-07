import collections.abc
import dataclasses as dc
import functools
import typing as ta

from .. import check
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactory
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactory
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
        if isinstance(spec, Generic) and spec.cls is list:  # type: ignore
            if (e := ctx.make(check.single(spec.args))) is None:
                return None  # type: ignore
            return IterableMarshaler(e)
        return None


@dc.dataclass(frozen=True)
class IterableUnmarshaler(Unmarshaler):
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Iterable:
        return list(map(functools.partial(self.e.unmarshal, ctx), check.isinstance(v, collections.abc.Iterable)))


class IterableUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, spec: Spec) -> ta.Optional[Unmarshaler]:
        if isinstance(spec, Generic) and spec.cls is list:  # type: ignore
            if (e := ctx.make(check.single(spec.args))) is None:
                return None  # type: ignore
            return IterableUnmarshaler(e)
        return None
