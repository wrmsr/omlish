from omlish.lite.cached import cached_nullary
from omlish.lite.inject import inj

from .inject import bind_interp
from .resolvers import InterpResolver


##


@cached_nullary
def get_default_interp_resolver() -> InterpResolver:
    return inj.create_injector(bind_interp())[InterpResolver]
