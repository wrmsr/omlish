import abc
import dataclasses as dc
import typing as ta

from .factories import Factory
from .factories import FuncFactory
from .factories import RecursiveSpecFactory
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


class RecursiveMarshalerFactory(RecursiveSpecFactory[Marshaler, MarshalContext]):
    def __init__(self, f: MarshalerFactory) -> None:
        def prx():
            m: ta.Optional[Marshaler] = None

            def inner(ctx, spec):
                if m is None:
                    raise TypeError('recursive proxy not set')
                return m(ctx, spec)

            def setm(r):
                nonlocal m
                m = r

            return inner, setm

        super().__init__(f, prx)


@dc.dataclass(frozen=True)
class SetType(RegistryItem):
    marshaler: ta.Optional[Marshaler] = None
    marshaler_factory: ta.Optional[MarshalerFactory] = None


