# ruff: noqa: PT009 PT027
# @omlish-lite
import subprocess
import unittest

from ...lite.check import check
from ..base import VerboseCalledProcessError
from ..sync import subprocesses


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

    def test_raise_verbose(self):
        try:
            subprocesses.check_output(
                'echo foo && false',
                shell=True,
            )
        except subprocess.CalledProcessError as e:
            self.assertFalse(isinstance(e, VerboseCalledProcessError))
        else:
            self.fail('Expected CalledProcessError')

        try:
            subprocesses.check_output(
                'echo foo && false',
                shell=True,
                raise_verbose=True,
            )
        except subprocess.CalledProcessError as e:
            self.assertTrue(isinstance(e, VerboseCalledProcessError))
            self.assertEqual(
                str(e),
                "Command '('echo foo && false',)' returned non-zero exit status 1. Output: b'foo\\n'",
            )
        else:
            self.fail('Expected CalledProcessError')
