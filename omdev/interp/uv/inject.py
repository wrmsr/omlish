# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

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
