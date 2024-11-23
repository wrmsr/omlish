# ruff: noqa: PT009 UP006 UP007
import os.path
import typing as ta
import unittest

from omlish.lite.inject import inj
from omlish.lite.logs import configure_standard_logging
from omlish.lite.runtime import is_debugger_attached

from ...configs import read_config_file
from ..configs import ServerConfig
from ..configs import prepare_server_config
from ..inject import bind_server
from ..spawningimpl import InheritedFds
from ..supervisor import Supervisor
from ..utils.utils import get_open_fds


class TestSupervisor(unittest.TestCase):
    def test_supervisor(self):
        inherited_fds: ta.Optional[InheritedFds] = None
        if is_debugger_attached():
            configure_standard_logging('DEBUG')
            inherited_fds = InheritedFds(get_open_fds(0x10000))

        #

        config_file = os.path.join(os.path.dirname(__file__), 'configs', 'demo.json')

        config = read_config_file(
            os.path.expanduser(config_file),
            ServerConfig,
            prepare=prepare_server_config,
        )

        #

        injector = inj.create_injector(bind_server(
            config,
            inherited_fds=inherited_fds,
        ))

        supervisor = injector.provide(Supervisor)

        #

        n = 0

        def callback(_):
            nonlocal n
            n += 1
            return n < 2

        supervisor.main(callback=callback)

        # FIXME: reap lol
        self.assertIsNotNone(supervisor)
