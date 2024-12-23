# ruff: noqa: UP006 UP007
import datetime
import json
import os.path
import tempfile
import unittest

from omlish.lite.inject import inj
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import OBJ_MARSHALER_MANAGER
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

from ..conf.specs import DeployAppConfFile
from ..conf.specs import DeployAppConfLink
from ..conf.specs import IniDeployAppConfContent
from ..conf.specs import JsonDeployAppConfContent
from ..conf.specs import NginxDeployAppConfContent
from ..config import DeployConfig
from ..deploy import DeployDriverFactory
from ..deploy import DeployManagerUtcClock
from ..git import DeployGitRepo
from ..inject import bind_deploy
from ..specs import DeployAppConfSpec
from ..specs import DeployAppLinksSpec
from ..specs import DeployAppSpec
from ..specs import DeployGitSpec
from ..specs import DeploySpec
from ..specs import DeploySystemdSpec
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
                    NginxDeployAppConfContent([
                        ['user', 'www', 'www'],
                        ['worker_processes', '2'],
                        ['events', [
                            ['worker_connections', '2000'],
                        ]],
                    ]),
                ),

                DeployAppConfFile(
                    'systemd/service.conf',
                    IniDeployAppConfContent({
                        'Unit': {
                            'After': 'default.target',
                        },
                        'Service': {
                            'ExecStart': 'sleep infinity',
                            'Restart': 'always',
                            'RestartSec': '1',
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
        rev=DeployRev('a2fc184a53ba524221b2443750c2493765d34efd'),
        subtrees=[
            'ominfra/scripts/supervisor.py',
        ],
    ),

    conf=DeployAppConfSpec(
        files=[
            DeployAppConfFile(
                'systemd.service',
                IniDeployAppConfContent({
                    'Unit': {
                        'After': 'default.target',
                    },
                    'Service': {
                        'ExecStart': '{app}/venv/bin/python ominfra/scripts/supervisor.py /dev/null',
                        'WorkingDirectory': '{app}',
                        'Restart': 'always',
                        'RestartSec': '1',
                    },
                    'Install': {
                        'WantedBy': 'default.target',
                    },
                }),

            ),
        ],
        links=[
            DeployAppConfLink('systemd.service'),
        ],
    ),
)


class TestDeploy(unittest.IsolatedAsyncioTestCase):
    async def test_deploy(self):
        deploy_home = DeployHome(os.path.join(tempfile.mkdtemp(), 'deploy'))

        systemd_unit_dir = tempfile.mkdtemp()

        print()
        print(f'{deploy_home=}')
        print(f'{systemd_unit_dir=}')
        print()

        #

        deploy_specs = [
            DeploySpec(
                home=deploy_home,
                apps=[
                    build_flask_thing_spec(rev='7bb3af10a21ac9c1884729638e1db765998cd7de'),
                    SUPERVISOR_SPEC,
                ],
                systemd=DeploySystemdSpec(
                    unit_dir=systemd_unit_dir,
                ),
            ),

            DeploySpec(
                home=deploy_home,
                apps=[
                    build_flask_thing_spec(rev='e9de238fc8cb73f7e0cc245139c0a45b33294fe3'),
                    SUPERVISOR_SPEC,
                ],
                systemd=DeploySystemdSpec(
                    unit_dir=systemd_unit_dir,
                ),
            ),

            DeploySpec(
                home=deploy_home,
                apps=[
                    SUPERVISOR_SPEC,
                ],
                app_links=DeployAppLinksSpec(
                    apps=[
                        DeployApp('flaskthing'),
                    ],
                ),
                systemd=DeploySystemdSpec(
                    unit_dir=systemd_unit_dir,
                ),
            ),
        ]

        #

        def new_utc_clock() -> DeployManagerUtcClock:
            clock_count = 0

            def utc_clock() -> datetime.datetime:
                now = datetime.datetime.now(tz=datetime.timezone.utc)  # noqa

                nonlocal clock_count
                then = now + datetime.timedelta(seconds=clock_count)
                clock_count += 1

                return then

            return DeployManagerUtcClock(utc_clock)  # type: ignore

        #

        injector = inj.create_injector(
            bind_deploy(
                deploy_config=DeployConfig(),
            ),

            inj.bind(OBJ_MARSHALER_MANAGER),

            inj.bind(new_utc_clock, singleton=True),
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
