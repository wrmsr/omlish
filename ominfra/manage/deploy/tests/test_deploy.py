# ruff: noqa: UP006 UP007
import os
import tempfile
import unittest

from omlish.lite.asyncio.subprocesses import asyncio_subprocess_run

from ..apps import DeployAppManager
from ..git import DeployGitManager
from ..git import DeployGitRepo
from ..types import DeployApp
from ..types import DeployHome
from ..types import DeployRev
from ..venvs import DeployVenvManager


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        if 'CI' in os.environ:
            await asyncio_subprocess_run('ssh', '-y', '-T', 'git@github.com')

        deploy_home = DeployHome(tempfile.mkdtemp())

        #

        app = DeployApp('flaskthing')
        rev = DeployRev('e9de238fc8cb73f7e0cc245139c0a45b33294fe3')

        repo = DeployGitRepo(
            host='github.com',
            path='wrmsr/flaskthing',
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
