"""
TODO:
 - poly
 - mappings
 - dc naming
"""
import abc
import dataclasses as dc
import typing as ta

from omlish import check

from .exc import UnhandledSpecException
from .factories import Factory
from .factories import RecursiveSpecFactory
from .registries import Registry
from .registries import RegistryItem
from .specs import Spec
from .specs import spec_of
from .utils import _Proxy
from .values import Value


##


class Marshaler(abc.ABC):
    @abc.abstractmethod
    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        raise NotImplementedError


class Unmarshaler(abc.ABC):
    @abc.abstractmethod
    def unmarshal(self, ctx: 'UnmarshalContext', v: Value) -> ta.Any:
        raise NotImplementedError


MarshalerFactory = Factory[Marshaler, 'MarshalContext', Spec]
UnmarshalerFactory = Factory[Unmarshaler, 'UnmarshalContext', Spec]


##


@dc.dataclass(frozen=True)
class FuncMarshaler(Marshaler):
    fn: ta.Callable[['MarshalContext', ta.Any], Value]

    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        return self.fn(ctx, o)


@dc.dataclass(frozen=True)
class FuncUnmarshaler(Unmarshaler):
    fn: ta.Callable[['UnmarshalContext', Value], ta.Any]

    def unmarshal(self, ctx: 'UnmarshalContext', v: Value) -> ta.Any:
        return self.fn(ctx, v)


##


@dc.dataclass(frozen=True)
class BaseContext(abc.ABC):
    registry: Registry


@dc.dataclass(frozen=True)
class MarshalContext(BaseContext):
    factory: ta.Optional[MarshalerFactory] = None

    def make(self, spec: Spec) -> Marshaler:
        spec = spec_of(spec)
        if (m := check.not_none(self.factory)(self, spec)) is not None:  # noqa
            return m
        raise UnhandledSpecException(spec)


@dc.dataclass(frozen=True)
class UnmarshalContext(BaseContext):
    factory: ta.Optional[UnmarshalerFactory] = None

    def make(self, spec: Spec) -> Unmarshaler:
        spec = spec_of(spec)
        if (m := check.not_none(self.factory)(self, spec)) is not None:  # noqa
            return m
        raise UnhandledSpecException(spec)


##


class _ProxyMarshaler(_Proxy[Marshaler], Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self._obj.marshal(ctx, o)


class RecursiveMarshalerFactory(RecursiveSpecFactory[Marshaler, MarshalContext]):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__(f, _ProxyMarshaler._new)  # noqa


class _ProxyUnmarshaler(_Proxy[Unmarshaler], Unmarshaler):
    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self._obj.unmarshal(ctx, v)


class RecursiveUnmarshalerFactory(RecursiveSpecFactory[Unmarshaler, UnmarshalContext]):
    def __init__(self, f: UnmarshalerFactory) -> None:
        super().__init__(f, _ProxyUnmarshaler._new)  # noqa


##


@dc.dataclass(frozen=True)
class SetType(RegistryItem):
    marshaler: ta.Optional[Marshaler] = None
    marshaler_factory: ta.Optional[MarshalerFactory] = None
