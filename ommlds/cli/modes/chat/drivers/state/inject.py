"""
TODO:
 - given chat-id + ephemeral = continue in mem
 - fork chats
"""
import os.path
import uuid

from omdev.home.paths import get_home_paths
from omlish import inject as inj

from ...... import minichain as mc
from .configs import StateConfig
from .ids import LastChatIdManager


##


def _new_chat_id() -> mc.drivers.ChatId:
    return mc.drivers.ChatId(uuid.uuid4())


async def _get_last_or_new_chat_id(lcim: LastChatIdManager) -> mc.drivers.ChatId:
    return lcid if (lcid := await lcim.get_last_chat_id()) is not None else _new_chat_id()


##


def _ensure_state_dir() -> str:
    state_dir = os.path.join(get_home_paths().state_dir, 'minichain', 'cli')
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
        os.chmod(state_dir, 0o770)  # noqa

    return state_dir


def _provide_json_file_state_storage() -> 'mc.drivers.StateStorage':
    state_dir = _ensure_state_dir()
    state_file = os.path.join(state_dir, 'state.json')
    return mc.drivers.JsonFileStateStorage(state_file)


def _provide_sql_state_storage() -> 'mc.drivers.StateStorage':
    state_dir = _ensure_state_dir()
    state_file = os.path.join(state_dir, 'state.db')
    # return mc.drivers.OrmStateStorage(mc.drivers.SqlStateStorage.Config(
    return mc.drivers.OrmStateStorage(mc.drivers.OrmStateStorage.Config(
        file=state_file,
    ))


##


def bind_state(cfg: StateConfig = StateConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    if cfg.format == 'json':
        els.append(inj.bind(_provide_json_file_state_storage, singleton=True))
    elif cfg.format == 'sql':
        els.append(inj.bind(_provide_sql_state_storage, singleton=True))
    else:
        raise ValueError(cfg.format)

    #

    if cfg.state in ('continue', 'new'):
        if cfg.state == 'new':
            els.append(inj.bind(mc.drivers.ChatId(uuid.UUID(cfg.chat_id)) if cfg.chat_id is not None else _new_chat_id()))  # noqa

        elif cfg.chat_id is not None:
            els.append(inj.bind(mc.drivers.ChatId(uuid.UUID(cfg.chat_id))))

        else:
            els.append(inj.bind(mc.drivers.ChatId, to_async_fn=_get_last_or_new_chat_id, singleton=True))

        els.extend([
            inj.bind(mc.drivers.build_driver_storage_key),
            inj.bind(mc.drivers.DriverStateManager, to_ctor=mc.drivers.StateStorageDriverStateManager, singleton=True),
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
            inj.bind(mc.drivers.DriverStateManager, to_ctor=mc.drivers.InMemoryDriverStateManager, singleton=True),
        ])

    else:
        raise TypeError(cfg.state)

    #

    return inj.as_elements(*els)
