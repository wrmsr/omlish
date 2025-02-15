import os.path

from omlish import lang

from ...home.paths import get_cache_dir
from .cache import Cache


##


@lang.cached_function(lock=True)
def default_dir() -> str:
    return os.path.join(get_cache_dir(), 'data')


@lang.cached_function(lock=True)
def default() -> Cache:
    return Cache(default_dir())
