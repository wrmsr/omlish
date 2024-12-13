# ruff: noqa: UP006 UP007
import tempfile
import unittest

from ..apps import DeployAppManager
from ..git import DeployGitManager
from ..git import DeployGitRepo
from ..types import DeployApp
from ..types import DeployHome
from ..types import DeployRev
from ..venvs import DeployVenvManager


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        #

        app = DeployApp('flaskthing')
        rev = DeployRev('c065adef7e27b56c3ecf6caec0edf24f59cf0790')

        repo = DeployGitRepo(
            host='github.com',
            path='piku/sample-python-app',
        )

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

        await apps.prepare_app(app, rev, repo)
