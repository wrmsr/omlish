import importlib.resources

from omlish import lang


@lang.cached_function
def favicon_bytes() -> bytes:
    return importlib.resources.files(__package__).joinpath('favicon.ico').read_bytes()
