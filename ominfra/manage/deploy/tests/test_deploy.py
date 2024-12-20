# ruff: noqa: UP006 UP007
import json
import os.path
import tempfile
import unittest

from omlish.lite.inject import inj
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

from ..conf.specs import DeployAppConfFile
from ..conf.specs import DeployAppConfLink
from ..conf.specs import IniDeployAppConfContent
from ..conf.specs import JsonDeployAppConfContent
from ..conf.specs import RawDeployAppConfContent
from ..config import DeployConfig
from ..driver import DeployDriverFactory
from ..git import DeployGitRepo
from ..inject import bind_deploy
from ..specs import DeployAppConfSpec
from ..specs import DeployAppSpec
from ..specs import DeployGitSpec
from ..specs import DeploySpec
from ..specs import DeployVenvSpec
from ..tags import DeployApp
from ..types import DeployHome
from ..types import DeployRev


def build_flask_thing_spec(
        *,
        rev: str,
) -> DeployAppSpec:
    return DeployAppSpec(
        app=DeployApp('flaskthing'),

        git=DeployGitSpec(
            repo=DeployGitRepo(
                host='github.com',
                path='wrmsr/flaskthing',
            ),
            rev=DeployRev(rev),
        ),

        venv=DeployVenvSpec(
            use_uv=True,
        ),

        conf=DeployAppConfSpec(
            files=[
                DeployAppConfFile(
                    'supervisor/sv.json',
                    JsonDeployAppConfContent({
                        'groups': {
                            'flaskthing': {
                                'processes': {
                                    'flaskthing': {
                                        'command': 'sleep 600',
                                    },
                                },
                            },
                        },
                    }),
                ),

                DeployAppConfFile(
                    'nginx.conf',
                    RawDeployAppConfContent('flaskthing nginx conf goes here'),
                ),

                DeployAppConfFile(
                    'systemd/service.conf',
                    IniDeployAppConfContent({
                        'Unit': {
                            'Description': "User-specific service to run 'sleep infinity'",
                            'After': 'default.target',
                        },
                        'Service': {
                            'ExecStart': '/bin/sleep infinity',
                            'Restart': 'always',
                            'RestartSec': '5',
                        },
                        'Install': {
                            'WantedBy': 'default.target',
                        },
                    }),
                ),
            ],

            links=[
                DeployAppConfLink('supervisor/'),
                DeployAppConfLink('supervisor/', kind='all_active'),

                DeployAppConfLink('nginx.conf'),
                DeployAppConfLink('nginx.conf', kind='all_active'),

                DeployAppConfLink('systemd/service.conf'),
                DeployAppConfLink('systemd/service.conf', kind='all_active'),
            ],
        ),
    )


SUPERVISOR_SPEC = DeployAppSpec(
    app=DeployApp('supervisor'),

    git=DeployGitSpec(
        repo=DeployGitRepo(
            host='github.com',
            path='wrmsr/omlish',
        ),
        rev=DeployRev('4dc487c3620d4629b8a2895a84511a4be478a801'),
        subtrees=[
            'ominfra/scripts/supervisor.py',
        ],
    ),

    conf=DeployAppConfSpec(
        files=[
            DeployAppConfFile(
                'systemd/service.conf',
                RawDeployAppConfContent('supervisor systemd conf goes here'),
            ),
        ],
        links=[
            DeployAppConfLink('systemd/service.conf'),
            DeployAppConfLink('systemd/service.conf', kind='all_active'),
        ],
    ),
)


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        deploy_home = DeployHome(os.path.join(tempfile.mkdtemp(), 'deploy'))

        print()
        print(deploy_home)
        print()

        #

        deploy_specs = [
            DeploySpec(
                home=deploy_home,
                apps=[
                    build_flask_thing_spec(rev='7bb3af10a21ac9c1884729638e1db765998cd7de'),
                    SUPERVISOR_SPEC,
                ],
            ),
            DeploySpec(
                home=deploy_home,
                apps=[
                    build_flask_thing_spec(rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3'),
                    SUPERVISOR_SPEC,
                ],
            ),
        ]

        #

        injector = inj.create_injector(
            bind_deploy(
                deploy_config=DeployConfig(),
            ),
        )

        #

        for _ in range(2):
            for spec in deploy_specs:
                print()

                sj = json_dumps_compact(marshal_obj(spec))
                print(sj)

                unmarshal_obj(json.loads(sj), DeploySpec)
                print()

                #

                with injector[DeployDriverFactory](spec) as driver:
                    await driver.drive_deploy()
