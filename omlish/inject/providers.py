import typing as ta

from .. import check
from .. import dataclasses as dc
from .types import Binding
from .types import Bindings
from .types import Key
from .types import Provider
from .types import ProviderFn
from .types import _BindingGen
from .types import _ProviderGen


def as_provider(o: ta.Any) -> Provider:
    check.not_isinstance(o, (Binding, _BindingGen, Bindings))
    if isinstance(o, _ProviderGen):
        return o._gen_provider()  # noqa
    return ConstProvider(type(o), o)


@dc.dataclass(frozen=True)
class FnProvider(Provider):
    cls: type
    fn: ProviderFn

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.cls

    def provider_fn(self) -> ProviderFn:
        return self.fn


@dc.dataclass(frozen=True)
class ConstProvider(Provider):
    cls: type
    v: ta.Any

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.cls

    def provider_fn(self) -> ProviderFn:
        return lambda _: self.v


@dc.dataclass(frozen=True)
class SingletonProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.p.provided_cls(rec)

    def provider_fn(self) -> ProviderFn:
        def fn(i):
            nonlocal v
            if v is not_set:
                v = pfn(i)
            return v

        pfn = self.p.provider_fn()
        v = not_set = object()
        return fn
