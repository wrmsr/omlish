from omlish import inject as inj

from .configs import StateConfig


##


def bind_state(cfg: StateConfig = StateConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    return inj.as_elements(*els)
