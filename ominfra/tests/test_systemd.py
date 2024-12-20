# @omlish-lite
import unittest

from ..systemd import render_systemd_unit


class TestSystemd(unittest.TestCase):
    def test_render_systemd_unit(self) -> None:
        sd_unit = {
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
        }

        print(render_systemd_unit(sd_unit))
