"""
TODO:
 - given chat-id + ephemeral = continue in mem
 - fork chats
"""
import uuid

from omlish import inject as inj

from ...... import minichain as mc
from .configs import StateConfig
from .ids import LastChatIdManager
from .storage import StateStorageDriverStateManager
from .storage import build_driver_storage_key


##


def _new_chat_id() -> mc.drivers.ChatId:
    return mc.drivers.ChatId(uuid.uuid4())


async def _get_last_or_new_chat_id(lcim: LastChatIdManager) -> mc.drivers.ChatId:
    return lcid if (lcid := await lcim.get_last_chat_id()) is not None else _new_chat_id()


##


def bind_state(cfg: StateConfig = StateConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.state in ('continue', 'new'):
        if cfg.state == 'new':
            els.append(inj.bind(mc.drivers.ChatId(uuid.UUID(cfg.chat_id)) if cfg.chat_id is not None else _new_chat_id()))  # noqa

        elif cfg.chat_id is not None:
            els.append(inj.bind(mc.drivers.ChatId(uuid.UUID(cfg.chat_id))))

        else:
            els.append(inj.bind(mc.drivers.ChatId, to_async_fn=_get_last_or_new_chat_id, singleton=True))

        els.extend([
            inj.bind(build_driver_storage_key),
            inj.bind(mc.drivers.StateManager, to_ctor=StateStorageDriverStateManager, singleton=True),
        ])

        #

        els.extend([
            inj.bind(LastChatIdManager, singleton=True),

            mc.drivers.injection.phase_callbacks().bind_item(to_fn=inj.target(
                lcim=LastChatIdManager,
                cid=mc.drivers.ChatId,
            )(lambda lcim, cid: mc.drivers.PhaseCallback(mc.drivers.Phase.STARTING, lambda: lcim.set_last_chat_id(cid)))),  # noqa
        ])

    elif cfg.state == 'ephemeral':
        if cfg.chat_id is not None:
            raise ValueError('chat-id is not allowed for ephemeral state')

        els.extend([
            inj.bind(_new_chat_id()),
            inj.bind(mc.drivers.StateManager, to_ctor=mc.drivers.InMemoryStateManager, singleton=True),
        ])

    else:
        raise TypeError(cfg.state)

    #

    return inj.as_elements(*els)
