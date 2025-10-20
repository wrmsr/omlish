from omlish import inject as inj
from omlish import lang

from .injection import phase_callbacks


with lang.auto_proxy_import(globals()):
    from . import manager as _manager


##


def bind_phases() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(phase_callbacks().bind_items_provider(singleton=True))

    #

    els.append(inj.bind(_manager.ChatPhaseManager, singleton=True))

    #

    return inj.as_elements(*els)
