import typing as ta

from ..providers import AsyncFnProvider
from ..providers import ConstProvider
from ..providers import CtorProvider
from ..providers import FnProvider
from ..providers import LinkProvider
from ..providers import Provider
from ..scopes import ScopeSeededProvider
from .inspect import build_kwargs_target
from .providers import AsyncCallableProviderImpl
from .providers import CallableProviderImpl
from .providers import ConstProviderImpl
from .providers import InternalProvider
from .providers import LinkProviderImpl
from .providers import ProviderImpl
from .scopes import ScopeSeededProviderImpl


##


PROVIDER_IMPLS_BY_PROVIDER: dict[type[Provider], ta.Callable[..., ProviderImpl]] = {
    AsyncFnProvider: lambda p: AsyncCallableProviderImpl(p, build_kwargs_target(p.fn)),
    FnProvider: lambda p: CallableProviderImpl(p, build_kwargs_target(p.fn)),
    CtorProvider: lambda p: CallableProviderImpl(p, build_kwargs_target(p.ty)),
    ConstProvider: ConstProviderImpl,
    LinkProvider: LinkProviderImpl,
    InternalProvider: lambda p: p.impl,

    ScopeSeededProvider: ScopeSeededProviderImpl,
}


def make_provider_impl(p: Provider) -> ProviderImpl:
    try:
        fac = PROVIDER_IMPLS_BY_PROVIDER[type(p)]
    except KeyError:
        pass
    else:
        return fac(p)

    raise TypeError(p)
