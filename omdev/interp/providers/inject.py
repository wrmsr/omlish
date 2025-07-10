# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .base import InterpProvider
from .base import InterpProviders
from .running import RunningInterpProvider
from .system import SystemInterpProvider


##


def bind_interp_providers() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind_array(InterpProvider),
        inj.bind_array_type(InterpProvider, InterpProviders),

        inj.bind(RunningInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=RunningInterpProvider, array=True),

        inj.bind(SystemInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=SystemInterpProvider, array=True),
    ]

    return inj.as_bindings(*lst)
