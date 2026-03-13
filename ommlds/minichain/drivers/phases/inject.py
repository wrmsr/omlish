from omlish import inject as inj

from .injection import phase_callbacks
from .manager import PhaseManager


##


def bind_phases() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(phase_callbacks().bind_items_provider(singleton=True))

    #

    els.append(inj.bind(PhaseManager, singleton=True))

    #

    return inj.as_elements(*els)
