# ruff: noqa: UP006 UP007
import os.path
import typing as ta

from omlish.lite.check import check
from omlish.lite.typing import Func1

from .apps import DeployAppManager
from .deploy import DeployManager
from .paths.manager import DeployPathsManager
from .specs import DeploySpec
from .tags import DeployAppRev
from .tags import DeployTagMap
from .types import DeployHome


class DeployDriverFactory(Func1[DeploySpec, ta.ContextManager['DeployDriver']]):
    pass


class DeployDriver:
    def __init__(
            self,
            *,
            spec: DeploySpec,

            deploys: DeployManager,
            paths: DeployPathsManager,
            apps: DeployAppManager,
    ) -> None:
        super().__init__()

        self._spec = spec

        self._deploys = deploys
        self._paths = paths
        self._apps = apps

    async def drive_deploy(self) -> None:
        self._paths.validate_deploy_paths()

        #

        hs = check.non_empty_str(self._spec.home)
        hs = os.path.expanduser(hs)
        hs = os.path.realpath(hs)
        hs = os.path.abspath(hs)

        home = DeployHome(hs)

        #

        deploy_tags = DeployTagMap(
            self._deploys.make_deploy_time(),
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
                home,
                app_tags,
            )
