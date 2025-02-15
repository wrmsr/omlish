"""
TODO:
 - XDG cache root
"""
import os.path


HOME_DIR_ENV_VAR = 'OMLISH_HOME'
DEFAULT_HOME_DIR = '~/.omlish'

CACHE_DIR_ENV_VAR = 'OMLISH_CACHE'
DEFAULT_CACHE_DIR = '~/.cache/omlish'


def get_home_dir() -> str:
    return os.path.expanduser(os.getenv(HOME_DIR_ENV_VAR, DEFAULT_HOME_DIR))


def get_cache_dir() -> str:
    return os.path.expanduser(os.getenv(DEFAULT_CACHE_DIR, DEFAULT_CACHE_DIR))
