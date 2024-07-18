import abc
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')
F = ta.TypeVar('F')


class FnPair(ta.Generic[F, T], abc.ABC):
    @abc.abstractmethod
    def forward(self, f: F) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def backward(self, t: T) -> F:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class FnPairImpl(FnPair[F, T]):
    forward: ta.Callable[[F], T]
    backward: ta.Callable[[T], F]

    def _forward(self, f: F) -> T:
        return self.forward(f)

    def _backward(self, t: T) -> F:
        return self.forward(t)


# HACK: ABC workaround. Our dataclasses handle this with override=True but we don't want to dep that in here.
FnPairImpl.forward = FnPairImpl._forward  # noqa
FnPairImpl.backward = FnPairImpl._backward  # noqa
FnPairImpl.__abstractmethods__ = frozenset()  # noqa


def of(forward: ta.Callable[[F], T], backward: ta.Callable[[T], F]) -> FnPair[F, T]:
    return FnPairImpl(forward, backward)


##


