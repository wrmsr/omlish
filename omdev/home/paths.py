# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - XDG cache root
"""
import os.path
import typing as ta


##


HOME_DIR_ENV_VAR = 'OMLISH_HOME'
DEFAULT_HOME_DIR = '~/.omlish'


def get_home_dir() -> str:
    return os.path.expanduser(os.getenv(HOME_DIR_ENV_VAR, DEFAULT_HOME_DIR))


#


class HomePaths:
    def __init__(self, home_dir: ta.Optional[str] = None) -> None:
        super().__init__()

        if home_dir is None:
            home_dir = get_home_dir()
        self._home_dir = home_dir

    @property
    def home_dir(self) -> str:
        return self._home_dir

    @property
    def config_dir(self) -> str:
        return os.path.join(self._home_dir, 'config')

    @property
    def log_dir(self) -> str:
        return os.path.join(self._home_dir, 'log')

    @property
    def run_dir(self) -> str:
        return os.path.join(self._home_dir, 'run')

    @property
    def shadow_dir(self) -> str:
        return os.path.join(self._home_dir, 'shadow')

    @property
    def state_dir(self) -> str:
        return os.path.join(self._home_dir, 'state')


def get_home_paths() -> HomePaths:
    return HomePaths()


##


CACHE_DIR_ENV_VAR = 'OMLISH_CACHE'
DEFAULT_CACHE_DIR = '~/.cache/omlish'


def get_cache_dir() -> str:
    return os.path.expanduser(os.getenv(DEFAULT_CACHE_DIR, DEFAULT_CACHE_DIR))
