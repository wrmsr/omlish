# @omlish-lite
import unittest

from omlish.text.indent import IndentWriter

from ..configs import NginxConfigItems
from ..configs import render_nginx_config


class TestConfigs(unittest.TestCase):
    def test_configs(self):
        conf = NginxConfigItems.of([
            ['user', 'www', 'www'],
            ['worker_processes', '2'],
            ['events', [
                ['worker_connections', '2000'],
            ]],
        ])

        wr = IndentWriter()
        render_nginx_config(wr, conf)
        print(wr.getvalue())
