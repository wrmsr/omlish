# ruff: noqa: PT009 UP006 UP007
import json
import os.path
import typing as ta
import unittest

from omlish.lite.logs import configure_standard_logging
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.runtime import is_debugger_attached

from ..compat import get_open_fds
from ..configs import ServerConfig
from ..context import ServerContext
from ..supervisor import Supervisor


class TestSupervisor(unittest.TestCase):
    def test_supervisor(self):
        initial_fds: ta.Optional[ta.FrozenSet[int]] = None
        if is_debugger_attached():
            configure_standard_logging('DEBUG')
            initial_fds = get_open_fds(0x10000)

        #

        config_file = os.path.join(os.path.dirname(__file__), 'demo.json')

        with open(config_file) as f:
            config_src = f.read()

        config_dct = json.loads(config_src)
        config: ServerConfig = unmarshal_obj(config_dct, ServerConfig)

        #

        context = ServerContext(
            config,
            inherited_fds=initial_fds,
        )
        supervisor = Supervisor(context)

        #

        n = 0

        def callback(_):
            nonlocal n
            n += 1
            return n < 2

        supervisor.setup()
        supervisor.run(callback=callback)

        # FIXME: reap lol
        self.assertIsNotNone(supervisor)
