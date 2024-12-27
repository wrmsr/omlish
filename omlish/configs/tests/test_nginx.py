# @omlish-lite
import unittest

from ..nginx import NginxConfigItems
from ..nginx import render_nginx_config_str


class TestConfigs(unittest.TestCase):
    def test_configs(self):
        conf = NginxConfigItems.of([
            ['user', 'www', 'www'],
            ['worker_processes', '2'],
            ['events', [
                ['worker_connections', '2000'],
            ]],
        ])

        print(render_nginx_config_str(conf))
