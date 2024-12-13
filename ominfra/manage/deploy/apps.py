# ruff: noqa: UP006 UP007
import datetime
import os.path
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check

from .git import DeployGitManager
from .git import DeployGitRepo
from .paths import DeployPath
from .paths import DeployPathOwner
from .specs import DeploySpec
from .types import DeployApp
from .types import DeployAppTag
from .types import DeployHome
from .types import DeployRev
from .types import DeployTag
from .venvs import DeployVenvManager


def make_deploy_tag(
        rev: DeployRev,
        now: ta.Optional[datetime.datetime] = None,
) -> DeployTag:
    if now is None:
        now = datetime.datetime.utcnow()  # noqa
    now_fmt = '%Y%m%dT%H%M%S'
    now_str = now.strftime(now_fmt)
    return DeployTag('-'.join([now_str, rev]))


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

    def get_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            DeployPath.parse('apps/@app/@tag'),
        }

    async def prepare_app(
            self,
            spec: DeploySpec,
    ):
        app_tag = DeployAppTag(spec.app, make_deploy_tag(spec.rev))
        app_dir = os.path.join(self._dir(), spec.app, app_tag.tag)

        #

        await self._git.checkout(
            spec.repo,
            spec.rev,
            app_dir,
        )

        #

        await self._venvs.setup_app_venv(app_tag)
