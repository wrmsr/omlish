# ruff: noqa: UP006 UP007
import datetime
import typing as ta

from omlish.lite.typing import Func0

from .apps import DeployAppManager
from .paths.manager import DeployPathsManager
from .specs import DeploySpec
from .tags import DeployAppRev
from .tags import DeployTagMap
from .tags import DeployTime


DEPLOY_TAG_DATETIME_FMT = '%Y%m%dT%H%M%SZ'


DeployManagerUtcClock = ta.NewType('DeployManagerUtcClock', Func0[datetime.datetime])


class DeployManager:
    def __init__(
            self,
            *,
            apps: DeployAppManager,
            paths: DeployPathsManager,

            utc_clock: ta.Optional[DeployManagerUtcClock] = None,
    ):
        super().__init__()

        self._apps = apps
        self._paths = paths

        self._utc_clock = utc_clock

    def _utc_now(self) -> datetime.datetime:
        if self._utc_clock is not None:
            return self._utc_clock()  # noqa
        else:
            return datetime.datetime.now(tz=datetime.timezone.utc)  # noqa

    def _make_deploy_time(self) -> DeployTime:
        return DeployTime(self._utc_now().strftime(DEPLOY_TAG_DATETIME_FMT))

    async def run_deploy(
            self,
            spec: DeploySpec,
    ) -> None:
        self._paths.validate_deploy_paths()

        #

        deploy_tags = DeployTagMap(
            self._make_deploy_time(),
            spec.key(),
        )

        #

        for app in spec.apps:
            app_tags = deploy_tags.add(
                app.app,
                app.key(),
                DeployAppRev(app.git.rev),
            )

            await self._apps.prepare_app(
                app,
                app_tags,
            )
