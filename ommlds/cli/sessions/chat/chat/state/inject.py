import typing as ta

from omlish import inject as inj
from omlish import lang

from ...phases.injection import phase_callbacks
from ...phases.types import ChatPhase
from ...phases.types import ChatPhaseCallback


with lang.auto_proxy_import(globals()):
    from . import inmemory as _inmemory
    from . import storage as _storage
    from . import types as _types


##


def bind_state(
        *,
        state: ta.Literal['new', 'continue', 'ephemeral'] = 'continue',
) -> inj.Elements:
    els: list[inj.Elemental] = []

    if state in ('continue', 'new'):
        els.append(inj.bind(_types.ChatStateManager, to_ctor=_storage.StateStorageChatStateManager, singleton=True))

        if state == 'new':
            els.append(phase_callbacks().bind_item(to_fn=lang.typed_lambda(cm=_types.ChatStateManager)(
                lambda cm: ChatPhaseCallback(ChatPhase.STARTING, cm.clear_state),
            )))

    elif state == 'ephemeral':
        els.append(inj.bind(_types.ChatStateManager, to_ctor=_inmemory.InMemoryChatStateManager, singleton=True))

    else:
        raise TypeError(state)

    return inj.as_elements(*els)
