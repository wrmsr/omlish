from .types import ChatEvent
from .types import ChatEventCallbacks


##


class ChatEventsManager:
    def __init__(self, callbacks: ChatEventCallbacks) -> None:
        super().__init__()

        self._callbacks = callbacks

    async def emit_event(self, event: ChatEvent) -> None:
        for cb in self._callbacks:
            await cb(event)
