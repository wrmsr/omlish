from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from ..chat.messages import UserChat
from ..events.types import Event
from .types import Action


##


@dc.dataclass(frozen=True)
@msh.update_fields_options(['action'], marshal_as=lang.OpaqueRepr, unmarshal_as=lang.OpaqueRepr)
class ActionEvent(Event, lang.Final):
    action: Action | lang.OpaqueRepr


##


@dc.dataclass(frozen=True)
class SendUserMessagesAction(Action, lang.Final):
    next_user_chat: UserChat


##


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, *[msh.OpenPolymorphismImpl(et) for et in [
        ActionEvent,
    ]])
