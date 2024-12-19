# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .inspect import InterpInspector
from .providers import InterpProvider
from .providers import InterpProviders
from .pyenv import PyenvInterpProvider
from .running import RunningInterpProvider


def bind_interp() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(InterpInspector, singleton=True),

        inj.bind_array(InterpProvider),
        inj.bind_array_type(InterpProvider, InterpProviders),

        inj.bind(PyenvInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=PyenvInterpProvider, array=True),

        inj.bind(RunningInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=RunningInterpProvider, array=True),
    ]

    return inj.as_bindings(*lst)
