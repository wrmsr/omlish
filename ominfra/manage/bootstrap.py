import dataclasses as dc

from .config import MainConfig
from .remote.config import RemoteConfig
from .system.config import SystemConfig


@dc.dataclass(frozen=True)
class MainBootstrap:
    main_config: MainConfig = MainConfig()

    remote_config: RemoteConfig = RemoteConfig()

    system_config: SystemConfig = SystemConfig()
