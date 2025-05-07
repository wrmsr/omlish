import os.path

from omdev.home.paths import get_home_paths
from omlish import inject as inj

from .sessions.base import Session
from .sessions.inject import bind_sessions
from .state import JsonFileStateStorage
from .state import StateStorage
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
        session_cfg: Session.Config,
        *,
        enable_test_weather_tool: bool = False,
) -> inj.Elements:
    els: list[inj.Elemental] = [
        bind_sessions(session_cfg),

        bind_tools(
            enable_test_weather_tool=enable_test_weather_tool,
        ),
    ]

    #

    els.append(inj.bind(_provide_state_storage, singleton=True))

    #

    return inj.as_elements(*els)
