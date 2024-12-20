# ruff: noqa: PT009 PT027 UP006 UP007
import unittest

from ...tags import DeployTagMap
from ..manager import DeployConfManager
from ..specs import DeployAppConfLink


class TestConf(unittest.TestCase):
    def test_compute_link(self):
        tags = DeployTagMap(
            time='time',
            app='app',
            app_key='app_key',
        )

        for lnk in [
            DeployAppConfLink('supervisor/'),
            DeployAppConfLink('supervisor/', kind='all_active'),

            DeployAppConfLink('nginx.conf'),
            DeployAppConfLink('nginx.conf', kind='all_active'),

            DeployAppConfLink('systemd/service.conf'),
            DeployAppConfLink('systemd/service.conf', kind='all_active'),
        ]:
            cl = DeployConfManager._compute_app_conf_link_dst(  # noqa
                lnk,
                tags,
                'app_conf_dir',
                'conf_link_dir',
            )
            print(cl)
