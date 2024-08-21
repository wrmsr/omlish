import collections.abc
import dataclasses as dc
import functools
import typing as ta

from .. import check
from .. import matchfns as mfs
from .. import reflect as rfl
from .base import MarshalContext
from .base import Marshaler
from .base import MarshalerFactoryMatchClass
from .base import UnmarshalContext
from .base import Unmarshaler
from .base import UnmarshalerFactoryMatchClass
from .values import Value


@dc.dataclass(frozen=True)
class IterableMarshaler(Marshaler):
    e: Marshaler

    def marshal(self, ctx: MarshalContext, o: ta.Iterable) -> Value:
        return list(map(functools.partial(self.e.marshal, ctx), o))


class IterableMarshalerFactory(MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable))
    def _build_generic(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler:
        if (e := ctx.make(check.single(rty.args))) is None:
            return None  # type: ignore
        return IterableMarshaler(e)

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, collections.abc.Iterable))
    def _build_concrete(self, ctx: MarshalContext, rty: rfl.Type) -> Marshaler | None:
        if (e := ctx.make(ta.Any)) is None:
            return None  # type: ignore
        return IterableMarshaler(e)


@dc.dataclass(frozen=True)
class IterableUnmarshaler(Unmarshaler):
    ctor: ta.Callable[[ta.Iterable[ta.Any]], ta.Iterable]
    e: Unmarshaler

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Iterable:
        return self.ctor(map(functools.partial(self.e.unmarshal, ctx), check.isinstance(v, collections.abc.Iterable)))


class IterableUnmarshalerFactory(UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: isinstance(rty, rfl.Generic) and issubclass(rty.cls, collections.abc.Iterable))
    def _build_generic(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler | None:
        if (e := ctx.make(check.single(rty.args))) is None:
            return None  # type: ignore
        return IterableUnmarshaler(rty.cls, e)  # noqa

    @mfs.simple(lambda _, ctx, rty: isinstance(rty, type) and issubclass(rty, collections.abc.Iterable))
    def _build_concrete(self, ctx: UnmarshalContext, rty: rfl.Type) -> Unmarshaler | None:
        if (e := ctx.make(ta.Any)) is None:
            return None  # type: ignore
        return IterableUnmarshaler(rty, e)  # noqa
