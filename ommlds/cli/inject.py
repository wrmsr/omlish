import os.path

from omdev.home.paths import get_home_paths
from omlish import inject as inj

from .backends.inject import bind_backends
from .sessions.base import Session
from .sessions.inject import bind_sessions
from .state import JsonFileStateStorage
from .state import StateStorage
from .tools.config import ToolsConfig
from .tools.inject import bind_tools


##


def _provide_state_storage() -> StateStorage:
    state_dir = os.path.join(get_home_paths().state_dir, 'minichain', 'cli')
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
        os.chmod(state_dir, 0o770)  # noqa

    state_file = os.path.join(state_dir, 'state.json')
    return JsonFileStateStorage(state_file)


##


def bind_main(
        *,
        session_cfg: Session.Config,
        tools_config: ToolsConfig,
        enable_backend_strings: bool = False,
) -> inj.Elements:
    els: list[inj.Elemental] = [
        bind_backends(
            enable_backend_strings=enable_backend_strings,
        ),

        bind_sessions(session_cfg),

        bind_tools(tools_config),
    ]

    #

    els.append(inj.bind(_provide_state_storage, singleton=True))

    #

    return inj.as_elements(*els)
