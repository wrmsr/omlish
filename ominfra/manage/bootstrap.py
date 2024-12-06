import dataclasses as dc

from omlish.lite.inject import Injector
from omlish.lite.inject import inj
from omlish.lite.logs import configure_standard_logging

from .config import MainConfig
from .inject import bind_main
from .remote import RemoteSpawning


##


@dc.dataclass(frozen=True)
class MainBootstrap:
    main_config: MainConfig

    remote_spawning_options: RemoteSpawning.Options


def main_bootstrap(bs: MainBootstrap) -> Injector:
    if (log_level := bs.main_config.log_level) is not None:
        configure_standard_logging(log_level)

    injector = inj.create_injector(bind_main(  # noqa
        main_config=bs.main_config,
        remote_spawning_options=bs.remote_spawning_options,
    ))

    return injector
