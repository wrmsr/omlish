# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.typing import Func1

from .apps import DeployAppManager
from .paths.manager import DeployPathsManager
from .specs import DeploySpec
from .tags import DeployAppRev
from .tags import DeployTagMap
from .tags import DeployTime
from .types import DeployHome


class DeployDriverFactory(Func1[DeploySpec, ta.ContextManager['DeployDriver']]):
    pass


class DeployDriver:
    def __init__(
            self,
            *,
            spec: DeploySpec,
            home: DeployHome,
            time: DeployTime,

            paths: DeployPathsManager,
            apps: DeployAppManager,
    ) -> None:
        super().__init__()

        self._spec = spec
        self._home = home
        self._time = time

        self._paths = paths
        self._apps = apps

    async def drive_deploy(self) -> None:
        self._paths.validate_deploy_paths()

        #

        deploy_tags = DeployTagMap(
            self._time,
            self._spec.key(),
        )

        #

        for app in self._spec.apps:
            app_tags = deploy_tags.add(
                app.app,
                app.key(),
                DeployAppRev(app.git.rev),
            )

            await self._apps.prepare_app(
                app,
                self._home,
                app_tags,
            )
