# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .ci import Ci


##


def bind_ci(
        *,
        config: Ci.Config,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(config),
        inj.bind(Ci, singleton=True),
    ]

    return inj.as_bindings(*lst)
