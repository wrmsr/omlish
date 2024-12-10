# ruff: noqa: PT009 PT027
import subprocess
import unittest

from .. import subprocesses as su
from ..check import check


class TestSubprocesses(unittest.TestCase):

    def test_subprocesses_call(self):
        su.subprocess_check_call('true')
        with self.assertRaises(subprocess.CalledProcessError):
            su.subprocess_check_call('false')
        self.assertTrue(su.subprocess_try_call('true'))
        self.assertFalse(su.subprocess_try_call('false'))

    def test_subprocesses_output(self):
        su.subprocess_check_output('echo', 'hi')
        try:
            su.subprocess_check_output('xcho', 'hi')
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        else:
            raise Exception('Expected exception')
        self.assertEqual(check.not_none(su.subprocess_try_output('echo', 'hi')).decode(), 'hi\n')
        self.assertIsNone(su.subprocess_try_output('xcho', 'hi'))
