# ruff: noqa: PT009 UP006 UP007
# @omlish-lite
import unittest

from ..systemd import SystemdListUnit


class TestSystemd(unittest.TestCase):
    def test_list_unit(self):
        s = """\
sleep-infinity.service         loaded    active running User-specific service to run 'sleep infinity'
supervisor.service             not-found active running supervisor.service
systemd-tmpfiles-setup.service loaded    active exited  Create User's Volatile Files and Directories
"""
        self.assertEqual(
            SystemdListUnit.parse_all(s),
            [
                SystemdListUnit(
                    unit='sleep-infinity.service',
                    load='loaded',
                    active='active',
                    sub='running',
                    description="User-specific service to run 'sleep infinity'",
                ),
                SystemdListUnit(
                    unit='supervisor.service',
                    load='not-found',
                    active='active',
                    sub='running',
                    description='supervisor.service',
                ),
                SystemdListUnit(
                    unit='systemd-tmpfiles-setup.service',
                    load='loaded',
                    active='active',
                    sub='exited',
                    description="Create User's Volatile Files and Directories",
                ),
            ],
        )
