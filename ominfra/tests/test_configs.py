# @omlish-lite
import unittest

from ..configs import render_ini_config


class TestSystemd(unittest.TestCase):
    def test_render_ini_config(self) -> None:
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

        print(render_ini_config(sd_unit))
