import abc
import dataclasses as dc
import typing as ta

from .factories import Factory
from .factories import RecursiveSpecFactory
from .registries import RegistryItem
from .specs import Spec
from .specs import spec_of
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


MarshalerFactory = Factory['MarshalContext', Spec, Marshaler]


@dc.dataclass(frozen=True)
class MarshalContext:
    marshaler_factory: ta.Optional[MarshalerFactory] = None

    def make(self, spec: Spec) -> Marshaler:
        return self.marshaler_factory(self, spec_of(spec))


class _ProxyFunc:
    _fn = None

    def __call__(self, *args, **kwargs):
        if self._fn is None:
            raise TypeError('recursive proxy not set')
        return self._fn(*args, **kwargs)

    def _set_fn(self, fn):
        if self._fn is not None:
            raise TypeError('recursive proxy already set')
        self._fn = fn

    @classmethod
    def _new(cls):
        return (p := cls()), p._set_fn


class _ProxyMarshaler(_ProxyFunc, Marshaler):
    marshal = _ProxyFunc.__call__


class RecursiveMarshalerFactory(RecursiveSpecFactory[Marshaler, MarshalContext]):
    def __init__(self, f: MarshalerFactory) -> None:
        super().__init__(f, _ProxyMarshaler._new)  # noqa


@dc.dataclass(frozen=True)
class SetType(RegistryItem):
    marshaler: ta.Optional[Marshaler] = None
    marshaler_factory: ta.Optional[MarshalerFactory] = None


