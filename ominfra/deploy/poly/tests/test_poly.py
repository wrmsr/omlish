import json
import tempfile
import unittest

from omlish.lite.json import json_dumps_compact
from omlish.lite.logs import configure_standard_logging  # noqa
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.runtime import is_debugger_attached  # noqa

from ..configs import DeployConfig
from ..configs import SiteConfig
from ..deploy import DeployImpl
from ..nginx import NginxDeployConcern
from ..nginx import NginxSiteConcern
from ..repo import RepoDeployConcern
from ..runtime import RuntimeImpl
from ..site import SiteImpl
from ..supervisor import SupervisorDeployConcern
from ..venv import VenvDeployConcern


class TestPolymorph(unittest.TestCase):
    def test_polymorph(self):
        if not is_debugger_attached():
            self.skipTest('debugger only')

        configure_standard_logging('DEBUG')

        print()

        root_dir = tempfile.mkdtemp('-ominfra-deploy-polymorph-test')
        print(root_dir)

        dcfg = DeployConfig(
            site=SiteConfig(
                root_dir=root_dir,
                concerns=[
                    NginxSiteConcern.Config(),
                ],
            ),
            name='omlish',
            concerns=[
                RepoDeployConcern.Config(
                    url='https://github.com/wrmsr/omlish',
                ),
                VenvDeployConcern.Config(
                    interp_version='3.12.5',
                ),
                SupervisorDeployConcern.Config(
                    entrypoint='app.server',
                ),
                NginxDeployConcern.Config(),
            ],
        )
        print(dcfg)

        jdcfg = json_dumps_compact(marshal_obj(dcfg))
        print(jdcfg)

        dcfg2: DeployConfig = unmarshal_obj(json.loads(jdcfg), DeployConfig)
        print(dcfg2)

        d = DeployImpl(
            dcfg2,
            SiteImpl(
                dcfg2.site,
            ),
        )
        print(d)

        d.run(RuntimeImpl())
