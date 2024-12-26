# @omlish-lite
import unittest

from ..sections import render_ini_sections


class TestIniRender(unittest.TestCase):
    def test_render_ini_sections(self) -> None:
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

        print(render_ini_sections(sd_unit))
