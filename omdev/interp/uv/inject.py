# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omcore.lite.inject import InjectorBindingOrBindings
from omcore.lite.inject import InjectorBindings
from omcore.lite.inject import inj

from ..providers.base import InterpProvider
from .provider import UvInterpProvider
from .uv import Uv


##


def bind_interp_uv() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(Uv, singleton=True),

        inj.bind(UvInterpProvider, singleton=True),
        inj.bind(InterpProvider, to_key=UvInterpProvider, array=True),
    ]

    return inj.as_bindings(*lst)
