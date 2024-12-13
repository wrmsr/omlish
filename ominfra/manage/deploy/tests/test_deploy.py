# ruff: noqa: UP006 UP007
import tempfile
import unittest

from omlish.lite.inject import inj

from ..apps import DeployAppManager
from ..config import DeployConfig
from ..git import DeployGitRepo
from ..inject import bind_deploy
from ..specs import DeploySpec
from ..types import DeployApp
from ..types import DeployHome
from ..types import DeployRev


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        deploy_config = DeployConfig(
            deploy_home=DeployHome(tempfile.mkdtemp()),
        )

        injector = inj.create_injector(
            bind_deploy(
                deploy_config=deploy_config,
            ),
        )

        #

        apps = injector[DeployAppManager]

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
