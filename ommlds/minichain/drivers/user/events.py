from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ...chat.messages import UserChat
from ...events.types import Event


##


@dc.dataclass(frozen=True)
class UserMessagesEvent(Event, lang.Final):
    chat: UserChat


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        UserMessagesEvent,
    ]])
