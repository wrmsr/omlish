# ruff: noqa: UP006 UP007
import datetime
import os.path
import tempfile
import typing as ta
import unittest

from ..git import DeployGitManager
from ..git import DeployGitRepo
from ..git import DeployGitSpec
from ..types import DeployApp
from ..types import DeployAppTag
from ..types import DeployHome
from ..types import DeployRev
from ..types import DeployTag
from ..venvs import DeployVenvManager


def make_deploy_tag(
        rev: DeployRev,
        now: ta.Optional[datetime.datetime] = None,
) -> DeployTag:
    if now is None:
        now = datetime.datetime.utcnow()  # noqa
    now_fmt = '%Y%m%dT%H%M%S'
    now_str = now.strftime(now_fmt)
    return DeployTag('-'.join([rev, now_str]))


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        app = DeployApp('flaskthing')
        rev = DeployRev('e9de238fc8cb73f7e0cc245139c0a45b33294fe3')

        repo = DeployGitRepo(
            host='github.com',
            path='wrmsr/flaskthing',
        )

        #

        app_tag = DeployAppTag(app, make_deploy_tag(rev))

        #

        git = DeployGitManager(deploy_home)

        spec = DeployGitSpec(
            repo=repo,
            rev=rev,
        )
        app_dir = os.path.join(deploy_home, 'apps', app, app_tag.tag)

        await git.checkout(spec, app_dir)

        #

        venvs = DeployVenvManager(deploy_home)

        await venvs.setup_app_venv(app_tag)
