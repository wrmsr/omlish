import abc
import dataclasses as dc
import typing as ta

from .factories import Factory
from .registries import RegistryItem
from .specs import Spec
from .values import Value


class Marshaler(abc.ABC):
    @abc.abstractmethod
    def __call__(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class FuncMarshaler(Marshaler):
    fn: ta.Callable[['MarshalContext', ta.Any], Value]

    def __call__(self, ctx: 'MarshalContext', o: ta.Any) -> Value:
        return self.fn(ctx, o)


MarshalerFactory = Factory['MarshalContext', Spec, Marshaler]


class MarshalContext:
    def make(self, spec: Spec) -> Marshaler:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class SetType(RegistryItem):
    marshaler: ta.Optional[Marshaler] = None
    marshaler_factory: ta.Optional[MarshalerFactory] = None
