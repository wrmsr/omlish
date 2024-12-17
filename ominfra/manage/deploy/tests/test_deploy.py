# ruff: noqa: UP006 UP007
import os.path
import tempfile
import unittest

from omlish.lite.inject import inj
from omlish.lite.json import json_dumps_pretty
from omlish.lite.strings import strip_with_newline

from ..config import DeployConfig
from ..deploy import DeployManager
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
                    DeployConfFile(
                        'nginx.conf',
                        'nginx conf goes here',
                    ),
                    DeployConfFile(
                        'systemd/service.conf',
                        'systemd conf goes here',
                    ),
                ],
                links=[
                    AppDeployConfLink('supervisor/'),
                    TagDeployConfLink('supervisor/'),

                    AppDeployConfLink('nginx.conf'),
                    TagDeployConfLink('nginx.conf'),

                    AppDeployConfLink('systemd/service.conf'),
                    TagDeployConfLink('systemd/service.conf'),
                ],
            ),
        )

        #

        from omlish.lite.json import json_dumps_compact
        from omlish.lite.marshal import marshal_obj
        print()
        print(json_dumps_compact(marshal_obj(spec)))
        print()

        #

        deploy_home = DeployHome(os.path.join(tempfile.mkdtemp(), 'deploy'))

        print(deploy_home)
        print()

        #

        injector = inj.create_injector(
            bind_deploy(
                deploy_config=DeployConfig(
                    deploy_home=deploy_home,
                ),
            ),
        )

        #

        await injector[DeployManager].deploy_app(spec)
