from omlish import inject as inj

from .injection import event_callbacks
from .manager import ChatEventsManager


##


def bind_events() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(event_callbacks().bind_items_provider(singleton=True))

    #

    els.append(inj.bind(ChatEventsManager, singleton=True))

    #

    return inj.as_elements(*els)
