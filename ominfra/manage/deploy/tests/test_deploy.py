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
from ..specs import CurrentOnlyDeployAppConfLink
from ..specs import DeployAppConfFile
from ..specs import DeployAppConfSpec
from ..specs import DeployAppSpec
from ..specs import DeployGitSpec
from ..specs import DeploySpec
from ..specs import DeployVenvSpec
from ..specs import AllActiveDeployAppConfLink
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
                DeployAppConfFile(
                    'nginx.conf',
                    'flaskthing nginx conf goes here',
                ),
                DeployAppConfFile(
                    'systemd/service.conf',
                    'flaskthing systemd conf goes here',
                ),
            ],
            links=[
                CurrentOnlyDeployAppConfLink('supervisor/'),
                AllActiveDeployAppConfLink('supervisor/'),

                CurrentOnlyDeployAppConfLink('nginx.conf'),
                AllActiveDeployAppConfLink('nginx.conf'),

                CurrentOnlyDeployAppConfLink('systemd/service.conf'),
                AllActiveDeployAppConfLink('systemd/service.conf'),
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
                'supervisor systemd conf goes here',
            ),
        ],
        links=[
            AllActiveDeployAppConfLink('systemd/service.conf'),
            CurrentOnlyDeployAppConfLink('systemd/service.conf'),
        ],
    ),
)


DEPLOY_SPECS = [
    DeploySpec(
        apps=[
            build_flask_thing_spec(rev='7bb3af10a21ac9c1884729638e1db765998cd7de'),
            SUPERVISOR_SPEC,
        ],
    ),
    DeploySpec(
        apps=[
            build_flask_thing_spec(rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3'),
            SUPERVISOR_SPEC,
        ],
    ),
]


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        # from omlish.lite.json import json_dumps_compact
        # from omlish.lite.marshal import marshal_obj
        # print()
        # print(json_dumps_compact(marshal_obj(FLASK_THING_SPEC)))
        # print()

        #

        deploy_home = DeployHome(os.path.join(tempfile.mkdtemp(), 'deploy'))

        print()
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

        for _ in range(2):
            for spec in DEPLOY_SPECS:
                await injector[DeployManager].run_deploy(spec)
