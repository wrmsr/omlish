from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ..chat.messages import UserChat
from ..events.types import Event
from .types import Action
from .types import DriverEvent


##


@dc.dataclass(frozen=True)
@msh.update_field_options(
    'action',
    marshal_via=msh.MarshalVia(lang.OpaqueRepr),
    unmarshal_via=msh.UnmarshalVia(lang.OpaqueRepr),
)
class ActionDriverEvent(DriverEvent, lang.Final):
    action: Action | lang.OpaqueRepr


##


@dc.dataclass(frozen=True)
class SendUserMessagesAction(Action, lang.Final):
    next_user_chat: UserChat


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        ActionDriverEvent,
    ]])
