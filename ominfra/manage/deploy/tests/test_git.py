import os.path
import tempfile
import unittest

from omlish.os.atomics import TempDirAtomicPathSwapping

from ..git import DeployGitManager
from ..git import DeployGitRepo
from ..specs import DeployGitSpec
from ..types import DeployHome


class TestGit(unittest.IsolatedAsyncioTestCase):
    async def test_git(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        git = DeployGitManager(
            deploy_home=deploy_home,
            atomics=TempDirAtomicPathSwapping(),
        )

        checkout = DeployGitSpec(
            repo=DeployGitRepo(
                host='github.com',
                path='wrmsr/flaskthing',
            ),
            rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3',
        )

        checkout_dir = os.path.join(deploy_home, 'apps', 'foo')
        print(checkout_dir)

        await git.checkout(
            checkout,
            checkout_dir,
        )

    async def test_git_subtree(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        git = DeployGitManager(
            deploy_home=deploy_home,
            atomics=TempDirAtomicPathSwapping(),
        )

        checkout = DeployGitSpec(
            repo=DeployGitRepo(
                host='github.com',
                path='wrmsr/flaskthing',
            ),
            rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3',
            subtrees=(
                'flaskthing/templates/*.html',
            ),
        )

        checkout_dir = os.path.join(deploy_home, 'apps', 'foo')
        print(checkout_dir)

        await git.checkout(
            checkout,
            checkout_dir,
        )
