# ruff: noqa: UP006 UP007
import datetime
import os.path
import typing as ta

from .git import DeployGitManager
from .git import DeployGitRepo
from .git import DeployGitSpec
from .paths import DeployPath
from .paths import DeployPathOwner
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
            deploy_home: DeployHome,
            git: DeployGitManager,
            venvs: DeployVenvManager,
    ) -> None:
        super().__init__()

        self._deploy_home = deploy_home
        self._git = git
        self._venvs = venvs

        self._dir = os.path.join(deploy_home, 'apps')

    def get_deploy_paths(self) -> ta.AbstractSet[DeployPath]:
        return {
            DeployPath.parse('apps/@app/@tag'),
        }

    async def prepare_app(
            self,
            app: DeployApp,
            rev: DeployRev,
            repo: DeployGitRepo,
    ):
        app_tag = DeployAppTag(app, make_deploy_tag(rev))
        app_dir = os.path.join(self._dir, app, app_tag.tag)

        #

        await self._git.checkout(
            DeployGitSpec(
                repo=repo,
                rev=rev,
            ),
            app_dir,
        )

        #

        await self._venvs.setup_app_venv(app_tag)
