import dataclasses as dc

from .config import MainConfig
from .remote.config import RemoteConfig


@dc.dataclass(frozen=True)
class MainBootstrap:
    main_config: MainConfig = MainConfig()

    remote_config: RemoteConfig = RemoteConfig()
