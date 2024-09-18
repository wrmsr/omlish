import os.path

from omlish import lang

from .cache import DataCache


##


@lang.cached_function(lock=True)
def default_dir() -> str:
    return os.path.expanduser('~/.cache/omlish/data')


@lang.cached_function(lock=True)
def default() -> DataCache:
    return DataCache(default_dir())
