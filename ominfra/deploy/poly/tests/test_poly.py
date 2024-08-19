import json
import tempfile
import unittest

from omlish.lite.json import json_dumps_compact
from omlish.lite.logs import configure_standard_logging  # noqa
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.runtime import is_debugger_attached  # noqa

from ..base import Deploy
from ..deploy import DeployImpl
from ..deploy import DeployRuntimeImpl
from ..nginx import NginxConcern
from ..repo import RepoConcern
from ..venv import VenvConcern


class TestPolymorph(unittest.TestCase):
    def test_polymorph(self):
        if not is_debugger_attached():
            self.skipTest('debugger only')

        configure_standard_logging('DEBUG')

        print()

        root_dir = tempfile.mkdtemp('-ominfra-deploy-polymorph-test')
        print(root_dir)

        dcfg = Deploy.Config(
            name='omlish',
            root_dir=root_dir,
            concerns=[
                RepoConcern.Config(
                    url='https://github.com/wrmsr/omlish',
                ),
                VenvConcern.Config(
                    interp_version='3.12.5',
                ),
                NginxConcern.Config(),
            ],
        )
        print(dcfg)

        jdcfg = json_dumps_compact(marshal_obj(dcfg))
        print(jdcfg)

        dcfg2: Deploy.Config = unmarshal_obj(json.loads(jdcfg), Deploy.Config)
        print(dcfg2)

        d = DeployImpl(
            dcfg2,
            runtime_cls=DeployRuntimeImpl,
        )
        print(d)

        d.run()
