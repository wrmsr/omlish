# ruff: noqa: PT009
import json
import os.path
import unittest

from omlish.lite.logs import configure_standard_logging
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.runtime import is_debugger_attached

from ..configs import ServerConfig
from ..context import ServerContext
from ..supervisor import Supervisor


class TestSupervisor(unittest.TestCase):
    def test_supervisor(self):
        if is_debugger_attached():
            configure_standard_logging('DEBUG')

        #

        config_file = os.path.join(os.path.dirname(__file__), 'demo.json')

        with open(config_file) as f:
            config_src = f.read()

        config_dct = json.loads(config_src)
        config: ServerConfig = unmarshal_obj(config_dct, ServerConfig)

        #

        context = ServerContext(config)
        supervisor = Supervisor(context)

        #

        n = 0

        def callback(_):
            nonlocal n
            n += 1
            return n > 1

        supervisor.setup()
        supervisor.run(callback=callback)

        self.assertIsNotNone(supervisor)
