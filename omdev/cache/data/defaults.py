import os.path

from omlish import lang

from .cache import Cache


##


@lang.cached_function(lock=True)
def default_dir() -> str:
    return os.path.expanduser('~/.cache/omlish/data')


@lang.cached_function(lock=True)
def default() -> Cache:
    return Cache(default_dir())
