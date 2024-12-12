import os.path
import tempfile
import unittest

from ..git import DeployGitManager
from ..git import DeployGitRepo
from ..git import DeployGitSpec
from ..types import DeployHome


class TestGit(unittest.IsolatedAsyncioTestCase):
    async def test_git(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        git = DeployGitManager(deploy_home)

        spec = DeployGitSpec(
            repo=DeployGitRepo(
                host='github.com',
                path='wrmsr/flaskthing',
            ),
            rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3',
        )
        checkout_dir = os.path.join(deploy_home, 'apps', 'foo')

        await git.checkout(spec, checkout_dir)
