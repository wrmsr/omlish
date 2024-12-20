# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj


def bind_interp_uv() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = []

    return inj.as_bindings(*lst)
