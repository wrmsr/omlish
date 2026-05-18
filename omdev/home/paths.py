# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
"""
TODO:
 - XDG cache root
"""
import enum
import os.path
import typing as ta

from omlish.os.environ import EnvVar


##


HOME_DIR_ENV_VAR = EnvVar('OMLISH_HOME')
DEFAULT_HOME_DIR = '~/.omlish'


def get_home_dir() -> str:
    return os.path.expanduser(HOME_DIR_ENV_VAR.get(DEFAULT_HOME_DIR))


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

    class DirKind(enum.Enum):
        HOME = 'home'
        CONFIG = 'config'
        LOG = 'log'
        RUN = 'run'
        SHADOW = 'shadow'
        STATE = 'state'

    config_subdir: ta.Final = 'config'
    log_subdir: ta.Final = 'log'
    run_subdir: ta.Final = 'run'
    shadow_subdir: ta.Final = 'shadow'
    state_subdir: ta.Final = 'state'

    _SUBDIR_BY_KIND: ta.Final[ta.Mapping[DirKind, str]] = {
        DirKind.HOME: '',
        DirKind.CONFIG: config_subdir,
        DirKind.LOG: log_subdir,
        DirKind.RUN: run_subdir,
        DirKind.SHADOW: shadow_subdir,
        DirKind.STATE: state_subdir,
    }

    def get_dir(self, kind: 'DirKind') -> str:
        return os.path.join(self._home_dir, self._SUBDIR_BY_KIND[kind])

    @property
    def config_dir(self) -> str:
        return self.get_dir(HomePaths.DirKind.CONFIG)

    @property
    def log_dir(self) -> str:
        return self.get_dir(HomePaths.DirKind.LOG)

    @property
    def run_dir(self) -> str:
        return self.get_dir(HomePaths.DirKind.RUN)

    @property
    def shadow_dir(self) -> str:
        return self.get_dir(HomePaths.DirKind.SHADOW)

    @property
    def state_dir(self) -> str:
        return self.get_dir(HomePaths.DirKind.STATE)


def get_home_paths() -> HomePaths:
    return HomePaths()


##


CACHE_DIR_ENV_VAR = EnvVar('OMLISH_CACHE')
DEFAULT_CACHE_DIR = '~/.cache/omlish'


def get_cache_dir() -> str:
    return os.path.expanduser(os.getenv(DEFAULT_CACHE_DIR, DEFAULT_CACHE_DIR))
