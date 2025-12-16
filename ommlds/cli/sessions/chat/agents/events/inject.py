from omlish import inject as inj
from omlish import lang

from .injection import event_callbacks


with lang.auto_proxy_import(globals()):
    from . import manager as _manager


##


def bind_events() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(event_callbacks().bind_items_provider(singleton=True))

    #

    els.append(inj.bind(_manager.ChatEventsManager, singleton=True))

    #

    return inj.as_elements(*els)
