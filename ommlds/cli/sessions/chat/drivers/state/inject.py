"""
TODO:
 - given chat-id + ephemeral = continue in mem
 - fork chats
"""
import uuid

from omlish import inject as inj
from omlish import lang

from ..phases.injection import phase_callbacks
from ..phases.types import ChatPhase
from ..phases.types import ChatPhaseCallback
from .configs import StateConfig


with lang.auto_proxy_import(globals()):
    from . import ids as _ids
    from . import inmemory as _inmemory
    from . import storage as _storage
    from . import types as _types


##


def _new_chat_id() -> '_types.ChatId':
    return _types.ChatId(uuid.uuid4())


async def _get_last_or_new_chat_id(lcim: '_ids.LastChatIdManager') -> '_types.ChatId':
    return lcid if (lcid := await lcim.get_last_chat_id()) is not None else _new_chat_id()


##


def bind_state(cfg: StateConfig = StateConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.state in ('continue', 'new'):
        if cfg.state == 'new':
            els.append(inj.bind(_types.ChatId(uuid.UUID(cfg.chat_id)) if cfg.chat_id is not None else _new_chat_id()))

        elif cfg.chat_id is not None:
            els.append(inj.bind(_types.ChatId(uuid.UUID(cfg.chat_id))))

        else:
            els.append(inj.bind(_types.ChatId, to_async_fn=_get_last_or_new_chat_id, singleton=True))

        els.extend([
            inj.bind(_storage.build_chat_storage_key),

            inj.bind(_types.ChatStateManager, to_ctor=_storage.StateStorageChatStateManager, singleton=True),
        ])

        #

        els.extend([
            inj.bind(_ids.LastChatIdManager, singleton=True),

            phase_callbacks().bind_item(to_fn=inj.target(
                lcim=_ids.LastChatIdManager,
                cid=_types.ChatId,
            )(lambda lcim, cid: ChatPhaseCallback(ChatPhase.STARTED, lambda: lcim.set_last_chat_id(cid)))),
        ])

    elif cfg.state == 'ephemeral':
        if cfg.chat_id is not None:
            raise ValueError('chat-id is not allowed for ephemeral state')

        els.extend([
            inj.bind(_new_chat_id()),

            inj.bind(_types.ChatStateManager, to_ctor=_inmemory.InMemoryChatStateManager, singleton=True),
        ])

    else:
        raise TypeError(cfg.state)

    #

    return inj.as_elements(*els)
