# ruff: noqa: UP006 UP007
import datetime
import typing as ta

from .apps import DeployAppManager
from .paths.manager import DeployPathsManager
from .specs import DeploySpec
from .types import DeployKey
from .types import DeployTag


DEPLOY_TAG_DATETIME_FMT = '%Y%m%dT%H%M%SZ'


def make_deploy_tag(
        key: DeployKey,
        *,
        utcnow: ta.Optional[datetime.datetime] = None,
) -> DeployTag:
    if utcnow is None:
        utcnow = datetime.datetime.now(tz=datetime.timezone.utc)  # noqa
    now_str = utcnow.strftime(DEPLOY_TAG_DATETIME_FMT)
    return DeployTag('-'.join([now_str, key]))


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

        tag = make_deploy_tag(spec.key())

        #

        for app in spec.apps:
            await self._apps.prepare_app(
                app,
                tag,
            )
