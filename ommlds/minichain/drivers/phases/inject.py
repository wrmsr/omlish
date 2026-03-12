from omlish import inject as inj

from .injection import phase_callbacks
from .manager import ChatPhaseManager


##


def bind_phases() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(phase_callbacks().bind_items_provider(singleton=True))

    #

    els.append(inj.bind(ChatPhaseManager, singleton=True))

    #

    return inj.as_elements(*els)
