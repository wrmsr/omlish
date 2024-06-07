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
class IterableMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Iterable) -> Value:
        return list(map(functools.partial(self.e.marshal, ctx), o))


class IterableMarshalerFactory(MarshalerFactory):
    def __call__(self, ctx: MarshalContext, rty: rfl.Type) -> ta.Optional[Marshaler]:
        if isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable):
            if (e := ctx.make(check.single(rty.args))) is None:
                return None  # type: ignore
            return IterableMarshaler(e)
        if isinstance(rty, type) and issubclass(rty, collections.abc.Iterable):
            if (e := ctx.make(ta.Any)) is None:
                return None  # type: ignore
            return IterableMarshaler(e)
        return None


@dc.dataclass(frozen=True)
class IterableUnmarshaler(Unmarshaler):
    ctor: ta.Callable[[ta.Iterable[ta.Any]], ta.Iterable]
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Iterable:
        return self.ctor(map(functools.partial(self.e.unmarshal, ctx), check.isinstance(v, collections.abc.Iterable)))


class IterableUnmarshalerFactory(UnmarshalerFactory):
    def __call__(self, ctx: UnmarshalContext, rty: rfl.Type) -> ta.Optional[Unmarshaler]:
        if isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable):
            if (e := ctx.make(check.single(rty.args))) is None:
                return None  # type: ignore
            return IterableUnmarshaler(rty.cls, e)  # noqa
        if isinstance(rty, type) and issubclass(rty, collections.abc.Iterable):
            if (e := ctx.make(ta.Any)) is None:
                return None  # type: ignore
            return IterableUnmarshaler(rty, e)  # noqa
        return None
