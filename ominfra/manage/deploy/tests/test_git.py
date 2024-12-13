import os.path
import tempfile
import unittest

from ..atomics import TempDirDeployAtomicPathSwapping
from ..git import DeployGitManager
from ..git import DeployGitRepo
from ..specs import DeployGitCheckout
from ..types import DeployHome
from ..types import DeployRev


class TestGit(unittest.IsolatedAsyncioTestCase):
    async def test_git(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        git = DeployGitManager(
            deploy_home=deploy_home,
            atomics=TempDirDeployAtomicPathSwapping(),
        )

        checkout = DeployGitCheckout(
            repo=DeployGitRepo(
                host='github.com',
                path='wrmsr/flaskthing',
            ),
            rev=DeployRev('e9de238fc8cb73f7e0cc245139c0a45b33294fe3'),
        )

        checkout_dir = os.path.join(deploy_home, 'apps', 'foo')

        await git.checkout(
            checkout,
            checkout_dir,
        )
