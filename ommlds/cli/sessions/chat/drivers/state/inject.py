"""
TODO:
 - given chat-id + ephemeral = continue in mem
 - fork chats
"""
import uuid

from omlish import check
from omlish import inject as inj
from omlish import lang

from .configs import StateConfig


with lang.auto_proxy_import(globals()):
    from . import inmemory as _inmemory
    from . import storage as _storage
    from . import types as _types


##


def _build_chat_storage_key(chat_id: '_types.ChatId') -> '_storage.ChatStateStorageKey':
    return _storage.ChatStateStorageKey(f'chat:{chat_id.v}')


def bind_state(cfg: StateConfig = StateConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.state in ('continue', 'new'):
        if cfg.state == 'new':
            els.append(inj.bind(_types.ChatId(uuid.uuid4())))
        else:
            els.append(inj.bind(_types.ChatId(uuid.UUID(check.non_empty_str(cfg.chat_id)))))

        els.extend([
            inj.bind(_build_chat_storage_key),

            inj.bind(_types.ChatStateManager, to_ctor=_storage.StateStorageChatStateManager, singleton=True),
        ])

    elif cfg.state == 'ephemeral':
        els.extend([
            inj.bind(_types.ChatId(uuid.uuid4())),

            inj.bind(_types.ChatStateManager, to_ctor=_inmemory.InMemoryChatStateManager, singleton=True),
        ])

    else:
        raise TypeError(cfg.state)

    return inj.as_elements(*els)
