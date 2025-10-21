import os.path

from omdev.home.paths import get_home_paths
from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import storage as _storage


##


def _provide_state_storage() -> '_storage.StateStorage':
    state_dir = os.path.join(get_home_paths().state_dir, 'minichain', 'cli')
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
        os.chmod(state_dir, 0o770)  # noqa

    state_file = os.path.join(state_dir, 'state.json')
    return _storage.JsonFileStateStorage(state_file)


def bind_state() -> inj.Elements:
    return inj.as_elements(
        inj.bind(_provide_state_storage, singleton=True),
    )
