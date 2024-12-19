import os.path
import tempfile
import unittest

from omlish.os.atomics import TempDirAtomicPathSwapping

from ..git import DeployGitManager
from ..git import DeployGitRepo
from ..specs import DeployGitSpec
from ..tmp import DeployHomeAtomics
from ..types import DeployHome
from ..types import DeployRev


class TestGit(unittest.IsolatedAsyncioTestCase):
    async def test_git(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        git = DeployGitManager(
            atomics=DeployHomeAtomics(lambda _: TempDirAtomicPathSwapping()),
        )

        checkout = DeployGitSpec(
            repo=DeployGitRepo(
                host='github.com',
                path='wrmsr/flaskthing',
            ),
            rev=DeployRev('e9de238fc8cb73f7e0cc245139c0a45b33294fe3'),
        )

        checkout_dir = os.path.join(deploy_home, 'apps', 'foo')
        print(checkout_dir)

        await git.checkout(
            checkout,
            deploy_home,
            checkout_dir,
        )

    async def test_git_subtree(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        git = DeployGitManager(
            atomics=DeployHomeAtomics(lambda _: TempDirAtomicPathSwapping()),
        )

        checkout = DeployGitSpec(
            repo=DeployGitRepo(
                host='github.com',
                path='wrmsr/flaskthing',
            ),
            rev=DeployRev('e9de238fc8cb73f7e0cc245139c0a45b33294fe3'),
            subtrees=(
                'flaskthing/templates/*.html',
            ),
        )

        checkout_dir = os.path.join(deploy_home, 'apps', 'foo')
        print(checkout_dir)

        await git.checkout(
            checkout,
            deploy_home,
            checkout_dir,
        )
