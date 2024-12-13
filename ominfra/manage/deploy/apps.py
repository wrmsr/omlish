# ruff: noqa: UP006 UP007
import datetime
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check

from .git import DeployGitManager
from .paths import DeployPath
from .paths import DeployPathOwner
from .specs import DeploySpec
from .types import DeployAppTag
from .types import DeployHome
from .types import DeployKey
from .types import DeployRev
from .types import DeployTag
from .venvs import DeployVenvManager


def make_deploy_tag(
        rev: DeployRev,
        key: DeployKey,
        *,
        utcnow: ta.Optional[datetime.datetime] = None,
) -> DeployTag:
    if utcnow is None:
        utcnow = datetime.datetime.now(tz=datetime.timezone.utc)  # noqa
    now_fmt = '%Y%m%dT%H%M%SZ'
    now_str = utcnow.strftime(now_fmt)
    return DeployTag('-'.join([now_str, rev, key]))


class DeployAppManager(DeployPathOwner):
    def __init__(
            self,
            *,
            deploy_home: ta.Optional[DeployHome] = None,
            git: DeployGitManager,
            venvs: DeployVenvManager,
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home
        self._git = git
        self._venvs = venvs

    @cached_nullary
    def _dir(self) -> str:
        return os.path.join(check.non_empty_str(self._deploy_home), 'apps')

    def get_owned_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            DeployPath.parse('apps/@app/@tag'),
        }

    async def prepare_app(
            self,
            spec: DeploySpec,
    ) -> None:
        app_tag = DeployAppTag(spec.app, make_deploy_tag(spec.checkout.rev, spec.key()))
        app_dir = os.path.join(self._dir(), spec.app, app_tag.tag)

        #

        await self._git.checkout(
            spec.checkout,
            app_dir,
        )

        #

        await self._venvs.setup_app_venv(app_tag)
