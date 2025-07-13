# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc

from .config import MainConfig
from .deploy.config import DeployConfig
from .remote.config import RemoteConfig
from .system.config import SystemConfig


##


@dc.dataclass(frozen=True)
class MainBootstrap:
    main_config: MainConfig = MainConfig()

    deploy_config: DeployConfig = DeployConfig()

    remote_config: RemoteConfig = RemoteConfig()

    system_config: SystemConfig = SystemConfig()
