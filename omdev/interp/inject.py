# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import Injector
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .inspect import InterpInspector
from .providers.inject import bind_interp_providers
from .pyenv.inject import bind_interp_pyenv
from .resolvers import InterpResolver
from .resolvers import InterpResolverProviders
from .uv.inject import bind_interp_uv


def bind_interp() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        bind_interp_providers(),

        bind_interp_pyenv(),

        bind_interp_uv(),

        inj.bind(InterpInspector, singleton=True),
    ]

    #

    def provide_interp_resolver_providers(injector: Injector) -> InterpResolverProviders:
        from .providers.running import RunningInterpProvider
        from .providers.system import SystemInterpProvider
        from .pyenv.pyenv import PyenvInterpProvider

        return InterpResolverProviders([((p := injector[c]).name, p) for c in [  # type: ignore
            PyenvInterpProvider,
            RunningInterpProvider,
            SystemInterpProvider,
        ]])

    lst.append(inj.bind(provide_interp_resolver_providers, singleton=True))

    lst.extend([
        inj.bind(InterpResolver, singleton=True),
    ])

    #

    return inj.as_bindings(*lst)
