import abc
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..injector import Injector
from ..providers import CtorProvider
from ..providers import FnProvider
from ..providers import Provider


class ProviderImpl(lang.Abstract):
    @property
    @abc.abstractmethod
    def provider(self) -> Provider:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, i: Injector) -> ta.Any:
        raise NotImplementedError


@dc.dataclass(frozen=True, eq=False)
class CallableProviderImpl(ProviderImpl):
    p: Provider
    fn: ta.Callable

    @property
    def provider(self) -> Provider:
        return self.p

    def provide(self, i: Injector) -> ta.Any:
        return i.inject(self.fn)  # TODO: cache kwargs_target


def make_provider_impl(p: Provider) -> ProviderImpl:
    if isinstance(p, CtorProvider):
        return CallableProviderImpl(p, p.cls)
    if isinstance(p, FnProvider):
        return CallableProviderImpl(p, p.fn)
    raise TypeError(p)
