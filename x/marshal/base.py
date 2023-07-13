import abc
import dataclasses as dc
import typing as ta

from omlish import check

from .exc import UnhandledSpecException
from .factories import Factory
from .factories import RecursiveSpecFactory
from .registries import RegistryItem
from .specs import Spec
from .specs import spec_of
from .utils import _Proxy
from .values import Value


class Marshaler(abc.ABC):
    @abc.abstractmethod
    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class FuncMarshaler(Marshaler):
    fn: ta.Callable[['MarshalContext', ta.Any], Value]

    def marshal(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        return self.fn(ctx, o)


MarshalerFactory = Factory[Marshaler, 'MarshalContext', Spec]


@dc.dataclass(frozen=True)
class MarshalContext:
    factory: ta.Optional[MarshalerFactory] = None

    def make(self, spec: Spec) -> Marshaler:
        spec = spec_of(spec)
        if (m := check.not_none(self.factory)(self, spec)) is not None:  # noqa
            return m
        raise UnhandledSpecException(spec)


class _ProxyMarshaler(_Proxy[Marshaler], Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return self._obj.marshal(ctx, o)


class RecursiveMarshalerFactory(RecursiveSpecFactory[Marshaler, MarshalContext]):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__(f, _ProxyMarshaler._new)  # noqa


@dc.dataclass(frozen=True)
class SetType(RegistryItem):
    marshaler: ta.Optional[Marshaler] = None
    marshaler_factory: ta.Optional[MarshalerFactory] = None
