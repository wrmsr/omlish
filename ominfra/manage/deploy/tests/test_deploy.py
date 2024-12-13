# ruff: noqa: UP006 UP007
import tempfile
import unittest

from ..apps import DeployAppManager
from ..git import DeployGitManager
from ..git import DeployGitRepo
from ..specs import DeploySpec
from ..types import DeployApp
from ..types import DeployHome
from ..types import DeployRev
from ..venvs import DeployVenvManager


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        #

        apps = DeployAppManager(
            deploy_home=deploy_home,
            git=DeployGitManager(
                deploy_home=deploy_home,
            ),
            venvs=DeployVenvManager(
                deploy_home=deploy_home,
            ),
        )

        #

        spec = DeploySpec(
            app=DeployApp('flaskthing'),
            repo=DeployGitRepo(
                host='github.com',
                path='wrmsr/flaskthing',
            ),
            rev=DeployRev('e9de238fc8cb73f7e0cc245139c0a45b33294fe3'),
        )

        await apps.prepare_app(spec)
