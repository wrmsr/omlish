# ruff: noqa: UP006 UP007
from .apps import DeployAppManager
from .paths.manager import DeployPathsManager
from .specs import DeploySpec


class DeployManager:
    def __init__(
            self,
            *,
            apps: DeployAppManager,
            paths: DeployPathsManager,
    ):
        super().__init__()

        self._apps = apps
        self._paths = paths

    async def run_deploy(
            self,
            spec: DeploySpec,
    ) -> None:
        self._paths.validate_deploy_paths()

        #

        await self._apps.prepare_app(spec)
