from omlish import inject as inj

from .injection import event_callbacks
from .manager import EventsManager
from .types import EventCallback


##


def bind_events() -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(event_callbacks().bind_items_provider(singleton=True))

    #

    els.extend([
        inj.bind(EventsManager, singleton=True),
        inj.bind(
            EventCallback,
            to_fn=inj.target(em=EventsManager)(lambda em: EventCallback(em.emit_event)),
            singleton=True,
        ),
    ])

    #

    return inj.as_elements(*els)
