import os.path

from omdev.home.paths import get_home_paths
from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import state
    from .backends import inject as backends_inj
    from .sessions import base as sessions_base
    from .sessions import inject as sessions_inj
    from .tools import config as tools_cfg
    from .tools import inject as tools_inj


##


def _provide_state_storage() -> 'state.StateStorage':
    state_dir = os.path.join(get_home_paths().state_dir, 'minichain', 'cli')
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
        os.chmod(state_dir, 0o770)  # noqa

    state_file = os.path.join(state_dir, 'state.json')
    return state.JsonFileStateStorage(state_file)


##


def bind_main(
        *,
        session_cfg: 'sessions_base.Session.Config',
        tools_config: 'tools_cfg.ToolsConfig',
        enable_backend_strings: bool = False,
) -> inj.Elements:
    els: list[inj.Elemental] = [
        backends_inj.bind_backends(
            enable_backend_strings=enable_backend_strings,
        ),

        sessions_inj.bind_sessions(session_cfg),

        tools_inj.bind_tools(tools_config),
    ]

    #

    els.append(inj.bind(_provide_state_storage, singleton=True))

    #

    return inj.as_elements(*els)
