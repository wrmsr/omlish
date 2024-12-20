# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .inspect import InterpInspector
from .providers.inject import bind_interp_providers
from .pyenv.inject import bind_interp_pyenv
from .uv.inject import bind_interp_uv


def bind_interp() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        bind_interp_providers(),

        bind_interp_pyenv(),

        bind_interp_uv(),

        inj.bind(InterpInspector, singleton=True),
    ]

    return inj.as_bindings(*lst)
