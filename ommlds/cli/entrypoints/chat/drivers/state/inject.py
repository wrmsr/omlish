"""
TODO:
 - given chat-id + ephemeral = continue in mem
 - fork chats
"""
import typing as ta
import uuid

from omlish import inject as inj
from omlish import orm

from ...... import minichain as mc
from .configs import StateConfig
from .last import LastChatIdManager
from .last import last_chat_id_mapper


##


def _new_chat_id() -> mc.drivers.ChatId:
    return mc.drivers.ChatId(uuid.uuid4())


async def _get_last_or_new_chat_id(lcm: LastChatIdManager) -> mc.drivers.ChatId:
    return cid if (cid := await lcm.get_last_chat_id()) is not None else _new_chat_id()


##


def bind_state(cfg: StateConfig = StateConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind_set_entry_const(ta.AbstractSet[orm.Mapper], last_chat_id_mapper()),
    ])

    #

    if cfg.state in ('continue', 'new'):
        if cfg.state == 'new':
            els.append(inj.bind(mc.drivers.ChatId(cfg.chat_id) if cfg.chat_id is not None else _new_chat_id()))

        elif cfg.chat_id is not None:
            els.append(inj.bind(mc.drivers.ChatId(cfg.chat_id)))

        else:
            els.append(inj.bind(mc.drivers.ChatId, to_async_fn=_get_last_or_new_chat_id, singleton=True))

        #

        els.extend([
            inj.bind(LastChatIdManager, singleton=True),

            mc.drivers.injection.phase_callbacks().bind_item(to_fn=inj.target(
                lcm=LastChatIdManager,
                cid=mc.drivers.ChatId,
            )(lambda lcm, cid: mc.drivers.PhaseCallback(mc.drivers.Phase.STARTING, lambda: lcm.set_last_chat_id(cid)))),  # noqa
        ])

    else:
        raise TypeError(cfg.state)

    #

    return inj.as_elements(*els)
