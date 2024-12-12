# ruff: noqa: PT009 PT027
import subprocess
import unittest

from ..check import check
from ..subprocesses import subprocesses


class TestSubprocesses(unittest.TestCase):

    def test_subprocesses_call(self):
        subprocesses.check_call('true')
        with self.assertRaises(subprocess.CalledProcessError):
            subprocesses.check_call('false')
        self.assertTrue(subprocesses.try_call('true'))
        self.assertFalse(subprocesses.try_call('false'))

    def test_subprocesses_output(self):
        subprocesses.check_output('echo', 'hi')
        try:
            subprocesses.check_output('xcho', 'hi')
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        else:
            raise Exception('Expected exception')
        self.assertEqual(check.not_none(subprocesses.try_output('echo', 'hi')).decode(), 'hi\n')
        self.assertIsNone(subprocesses.try_output('xcho', 'hi'))
