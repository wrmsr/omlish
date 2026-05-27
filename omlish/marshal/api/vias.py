import dataclasses as dc
import typing as ta

from ... import check
from ... import lang
from ... import metadata as md
from ... import reflect as rfl
from ... import typedvalues as tv
from .configs import Config
from .contexts import MarshalFactoryContext
from .contexts import UnmarshalFactoryContext
from .errors import UnhandledTypeError
from .types import Marshaler
from .types import MarshalerFactory
from .types import Unmarshaler
from .types import UnmarshalerFactory


T = ta.TypeVar('T')


##


@ta.final
@dc.dataclass(frozen=True)
class MarshalVia(tv.UniqueTypedValue, Config, lang.Final):
    o: MarshalerFactory | Marshaler | ta.Any

    def __post_init__(self) -> None:
        check.not_none(self.o)


@ta.final
@dc.dataclass(frozen=True)
class UnmarshalVia(tv.UniqueTypedValue, Config, lang.Final):
    o: UnmarshalerFactory | Unmarshaler | ta.Any

    def __post_init__(self) -> None:
        check.not_none(self.o)


def kw_marshal_via(o: MarshalerFactory | Marshaler | ta.Any) -> ta.Any:
    return dict(marshal_via=MarshalVia(o))


def kw_unmarshal_via(o: UnmarshalerFactory | Unmarshaler | ta.Any) -> ta.Any:
    return dict(unmarshal_via=UnmarshalVia(o))


def kw_marshal_unmarshal_via(o: ta.Any) -> ta.Any:
    return dict(
        marshal_via=MarshalVia(o),
        unmarshal_via=UnmarshalVia(o),
    )


##


def make_marshaler_via(ctx: MarshalFactoryContext, rty: rfl.Type, via: MarshalVia) -> Marshaler:
    o = via.o

    if isinstance(o, Marshaler):
        return o

    if isinstance(o, MarshalerFactory):
        if (m := o.make_marshaler(ctx, rty)) is None:
            raise UnhandledTypeError(rty)
        return m()

    return ctx.make_marshaler(o)


def make_unmarshaler_via(ctx: UnmarshalFactoryContext, rty: rfl.Type, via: UnmarshalVia) -> Unmarshaler:
    o = via.o

    if isinstance(o, Unmarshaler):
        return o

    if isinstance(o, UnmarshalerFactory):
        if (m := o.make_unmarshaler(ctx, rty)) is None:
            raise UnhandledTypeError(rty)
        return m()

    return ctx.make_unmarshaler(o)


##


@dc.dataclass(frozen=True)
class _MarshalViaMetadata(md.ClassDecoratorObjectMetadata, lang.Final):
    via: MarshalVia


@dc.dataclass(frozen=True)
class _UnmarshalViaMetadata(md.ClassDecoratorObjectMetadata, lang.Final):
    via: UnmarshalVia


def set_marshal_via(o: MarshalerFactory | Marshaler | ta.Any) -> ta.Callable[[type[T]], type[T]]:
    def inner(cls):
        _MarshalViaMetadata(MarshalVia(o))(cls)
        return cls
    return inner


def set_unmarshal_via(o: UnmarshalerFactory | Unmarshaler | ta.Any) -> ta.Callable[[type[T]], type[T]]:
    def inner(cls):
        _UnmarshalViaMetadata(UnmarshalVia(o))(cls)
        return cls
    return inner
