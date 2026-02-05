import os.path

from omdev.home.paths import get_home_paths
from omlish import inject as inj
from omlish import lang

from .configs import StateConfig


with lang.auto_proxy_import(globals()):
    from . import json as _json
    from . import sql as _sql
    from . import storage as _storage


##


def _ensure_state_dir() -> str:
    state_dir = os.path.join(get_home_paths().state_dir, 'minichain', 'cli')
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
        os.chmod(state_dir, 0o770)  # noqa

    return state_dir


def _provide_json_file_state_storage() -> '_storage.StateStorage':
    state_dir = _ensure_state_dir()
    state_file = os.path.join(state_dir, 'state.json')
    return _json.JsonFileStateStorage(state_file)


def _provide_sql_state_storage() -> '_storage.StateStorage':
    state_dir = _ensure_state_dir()
    state_file = os.path.join(state_dir, 'state.db')
    return _sql.SqlStateStorage(_sql.SqlStateStorage.Config(
        file=state_file,
    ))


def bind_state(cfg: StateConfig = StateConfig()) -> inj.Elements:
    lst: list[inj.Elemental] = []

    if cfg.format == 'json':
        lst.append(inj.bind(_provide_json_file_state_storage, singleton=True))
    elif cfg.format == 'sql':
        lst.append(inj.bind(_provide_sql_state_storage, singleton=True))
    else:
        raise ValueError(cfg.format)

    return inj.as_elements(*lst)
