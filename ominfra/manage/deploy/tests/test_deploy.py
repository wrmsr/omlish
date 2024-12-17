# ruff: noqa: UP006 UP007
import tempfile
import unittest

from omlish.lite.inject import inj
from omlish.lite.json import json_dumps_pretty
from omlish.lite.strings import strip_with_newline

from ..apps import DeployAppManager
from ..config import DeployConfig
from ..git import DeployGitRepo
from ..inject import bind_deploy
from ..paths import DeployPathOwners
from ..specs import AppDeployConfLink
from ..specs import DeployConfFile
from ..specs import DeployConfSpec
from ..specs import DeployGitSpec
from ..specs import DeploySpec
from ..specs import DeployVenvSpec
from ..specs import TagDeployConfLink
from ..types import DeployApp
from ..types import DeployHome
from ..types import DeployRev


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        deploy_home = DeployHome(tempfile.mkdtemp())

        print()
        print(deploy_home)
        print()

        #

        deploy_config = DeployConfig(
            deploy_home=deploy_home,
        )

        injector = inj.create_injector(
            bind_deploy(
                deploy_config=deploy_config,
            ),
        )

        #

        print(injector[DeployPathOwners])

        #

        apps = injector[DeployAppManager]

        #

        spec = DeploySpec(
            app=DeployApp('flaskthing'),

            git=DeployGitSpec(
                repo=DeployGitRepo(
                    host='github.com',
                    path='wrmsr/flaskthing',
                ),
                rev=DeployRev('e9de238fc8cb73f7e0cc245139c0a45b33294fe3'),
            ),

            venv=DeployVenvSpec(
                use_uv=True,
            ),

            conf=DeployConfSpec(
                files=[
                    DeployConfFile(
                        'supervisor/flaskthing.json',
                        strip_with_newline(json_dumps_pretty({
                            'groups': {
                                'flaskthing': {
                                    'processes': {
                                        'flaskthing': {
                                            'command': 'sleep 600',
                                        },
                                    },
                                },
                            },
                        })),
                    ),
                ],
                links=[
                    AppDeployConfLink('supervisor/'),
                    TagDeployConfLink('supervisor/'),
                    AppDeployConfLink('supervisor/flaskthing.json'),
                    TagDeployConfLink('supervisor/flaskthing.json'),
                ],
            ),
        )

        #

        from omlish.lite.json import json_dumps_compact
        from omlish.lite.marshal import marshal_obj
        print(json_dumps_compact(marshal_obj(spec)))

        #

        await apps.prepare_app(spec)
