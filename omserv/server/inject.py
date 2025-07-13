import functools

from omlish import inject as inj

from .config import Config
from .server import Server
from .server import ServerFactory


##


def _provide_server_factory(config: Config) -> ServerFactory:
    return ServerFactory(functools.partial(Server, config=config))


def bind_server(
        config: Config,
) -> inj.Elemental:
    return inj.as_elements(
        inj.bind(config),

        inj.bind(_provide_server_factory, singleton=True),
    )
