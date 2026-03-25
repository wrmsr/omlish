from omlish import marshal as msh

from ..types import Event


##


class EventLogger:
    async def handle_event(self, event: Event) -> None:
        msh.marshal(event, Event)
