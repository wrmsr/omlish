# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omcore.lite.inject import InjectorBindingOrBindings
from omcore.lite.inject import InjectorBindings
from omcore.lite.inject import inj


##


def bind_pyproject() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = []

    return inj.as_bindings(*lst)
