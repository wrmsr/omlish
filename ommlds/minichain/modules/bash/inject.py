from omlish import inject as inj

from .configs import BashConfig


##


def bind_bash(cfg: BashConfig = BashConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    return inj.as_elements(*els)
