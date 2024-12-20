# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..providers.base import InterpProvider
from .provider import PyenvInterpProvider
from .pyenv import Pyenv


def bind_interp_pyenv() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(Pyenv, singleton=True),

        inj.bind(PyenvInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=PyenvInterpProvider, array=True),
    ]

    return inj.as_bindings(*lst)
