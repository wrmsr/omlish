# ruff: noqa: I001
# fmt: off
import pytest

from . import (  # noqa
    asyncs,
    depskip,
    logging,
    managermarks,
    pydevd,
    repeat,
    skips,
    spacing,
    switches,
)

from ._registry import (  # noqa
    ALL,
    register,
)


def add_hooks(pm: pytest.PytestPluginManager) -> None:
    present_types = {type(p) for p in pm.get_plugins()}

    for plugin in ALL:
        if plugin not in present_types:
            pm.register(plugin())  # noqa
