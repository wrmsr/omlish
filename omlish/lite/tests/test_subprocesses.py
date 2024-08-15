# ruff: noqa: PT009 PT027
import subprocess
import unittest

from .. import subprocesses as su
from ..check import check_not_none


class TestSubprocesses(unittest.TestCase):

    def test_subprocesses_call(self):
        su.subprocess_check_call('true')
        with self.assertRaises(subprocess.CalledProcessError):
            su.subprocess_check_call('false')
        self.assertTrue(su.subprocess_try_call('true'))
        self.assertFalse(su.subprocess_try_call('false'))

    def test_subprocesses_output(self):
        su.subprocess_check_output('echo', 'hi')
        with self.assertRaises(
                FileNotFoundError if not su._SUBPROCESS_SHELL_WRAP_EXECS else subprocess.CalledProcessError,  # noqa
        ):
            su.subprocess_check_output('xcho', 'hi')
        self.assertEqual(check_not_none(su.subprocess_try_output('echo', 'hi')).decode(), 'hi\n')
        self.assertIsNone(su.subprocess_try_output('xcho', 'hi'))
