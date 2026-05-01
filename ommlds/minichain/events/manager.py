from .types import Event
from .types import EventCallbacks


##


class EventsManager:
    def __init__(self, callbacks: EventCallbacks) -> None:
        super().__init__()

        self._callbacks = callbacks

    async def emit_event(self, event: Event) -> None:
        for cb in self._callbacks:
            await cb(event)
