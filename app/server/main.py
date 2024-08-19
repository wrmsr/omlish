import enum

from omlish import dataclasses as dc
from omlish import inject as inj
from omserv.apps.base import BaseServerUrl

from .. import shell
from ..dbs import bind_dbs
from ..secrets import bind_secrets
from .inject import bind_app
from .inject import bind_db_user_store
from .inject import bind_in_memory_user_store


class UserStoreKind(enum.Enum):
    IN_MEMORY = enum.auto()
    DB = enum.auto()


@dc.dataclass(frozen=True)
class ServerConfig:
    user_store: UserStoreKind = UserStoreKind.IN_MEMORY

    node_registry_enabled: bool = False

    base_server_url: str = 'http://localhost:8000/'


def bind_user_store(cfg: ServerConfig) -> inj.Elemental:
    match cfg.user_store:
        case UserStoreKind.IN_MEMORY:
            return bind_in_memory_user_store()
        case UserStoreKind.DB:
            return bind_db_user_store()
    raise ValueError(cfg.user_store)


def _main(cfg: ServerConfig = ServerConfig()) -> None:
    shell.run_shell(
        shell.bind_asgi_server(bind_app()),

        *([shell.bind_node_registrant()] if cfg.node_registry_enabled else []),

        bind_dbs(),

        bind_secrets(),

        bind_user_store(cfg),

        inj.bind(cfg),
        inj.bind(BaseServerUrl, to_const=BaseServerUrl(cfg.base_server_url)),
    )


if __name__ == '__main__':
    _main()
