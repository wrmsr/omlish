import os.path

from omdev.home.paths import get_home_paths
from omlish import inject as inj

from .sessions.base import Session
from .state import JsonFileStateStorage
from .state import StateStorage


##


def _provide_state_storage() -> StateStorage:
    state_dir = os.path.join(get_home_paths().state_dir, 'minichain', 'cli')
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
        os.chmod(state_dir, 0o770)  # noqa

    state_file = os.path.join(state_dir, 'state.json')
    return JsonFileStateStorage(state_file)


##


def bind_main(session_cfg: Session.Config) -> inj.Elements:
    els: list[inj.Elemental] = [
        inj.bind(session_cfg),
        inj.bind(session_cfg.configurable_cls, singleton=True),
        inj.bind(Session, to_key=session_cfg.configurable_cls),
    ]

    #

    els.append(inj.bind(_provide_state_storage, singleton=True))

    #

    return inj.as_elements(*els)
