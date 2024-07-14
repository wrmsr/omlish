"""
Given their special status, these are more formal than other interfaces (which increasingly tend to just be callables
taking a dataclass, in which Nop* is just void).

We want to support and balance the following:
 - contextual (threadlocal and.. 'otherwise') overriding
 - not needing to propagate kwargs
 - injection friendliness, yet with sane injectorless defaults
 - honoring the 'log' module-global idiom, largely for interop with embedding

TODO:
 - def runtime.log -> caller lookup :/ like stdlib does lols
 - inheritable thread local
 - ~tracing~
"""
import abc

from .facets.errors import Errors
from .facets.logging import Logger
from .facets.metrics import Metrics


class Runtime(abc.ABC):

    @abc.abstractproperty
    def errors(self) -> Errors:
        raise NotImplementedError

    @abc.abstractproperty
    def log(self) -> Logger:
        raise NotImplementedError

    @abc.abstractproperty
    def metrics(self) -> Metrics:
        raise NotImplementedError

    def __getstate__(self):
        raise TypeError(self)


class ProxyRuntime(Runtime):
    def __init__(self, underlying: Runtime) -> None:
        super().__init__()
        if not isinstance(underlying, Runtime):
            raise TypeError(underlying)
        self._underlying = underlying

    @property
    def underlying(self) -> Runtime:
        return self._underlying

    @underlying.setter
    def underlying(self, underlying: Runtime) -> None:
        if not isinstance(underlying, Runtime):
            raise TypeError(underlying)
        self._underlying = underlying

    def errors(self) -> Errors:
        return self._underlying.errors

    def log(self) -> Logger:
        return self._underlying.log

    def metrics(self) -> Metrics:
        return self._underlying.metrics


class InvalidRuntime(Runtime):

    def errors(self) -> Errors:
        raise RuntimeError(self)

    def log(self) -> Logger:
        raise RuntimeError(self)

    def metrics(self) -> Metrics:
        raise RuntimeError(self)


class InvalidatableRuntime(ProxyRuntime):

    def __init__(self, underlying: Runtime) -> None:
        super().__init__(underlying)
        self._is_invalidated = False

    @property
    def is_invalidated(self) -> bool:
        return self._is_invalidated

    def invalidate(self) -> None:
        if not self._is_invalidated:
            self._is_invalidated = True
            self._underlying = InvalidRuntime()

    @property
    def underlying(self) -> Runtime:
        if self._is_invalidated:
            raise RuntimeError(self)
        return self._underlying

    @underlying.setter
    def underlying(self, underlying: Runtime) -> None:
        if self._is_invalidated:
            raise RuntimeError(self)
        if not isinstance(underlying, Runtime):
            raise TypeError(underlying)
        self._underlying = underlying
