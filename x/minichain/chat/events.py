from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ..events.types import Event
from .messages import Chat
from .messages import UserChat


##


@dc.dataclass(frozen=True)
class UserMessagesEvent(Event, lang.Final):
    chat: UserChat


@dc.dataclass(frozen=True)
class AiMessagesEvent(Event, lang.Final):
    chat: Chat

    _: dc.KW_ONLY

    streamed: bool = False


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        UserMessagesEvent,
        AiMessagesEvent,
    ]])
