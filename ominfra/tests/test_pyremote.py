# ruff: noqa: PT009
# @omlish-lite
import os.path
import subprocess
import sys
import unittest

from omlish.lite.check import check_not_none
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from .. import pyremote


class TestPyremote(unittest.TestCase):
    def test_pyremote(self):
        with open(os.path.join(os.path.dirname(__file__), '..', 'pyremote.py')) as f:
            pyr_src = f.read()

        main_src = '\n'.join([
            pyr_src,
            'rt = pyremote_bootstrap_finalize()',
            'b = rt.input.read()',
            'os.write(1, b"!" + b + b"!")',
        ])

        #

        proc = subprocess.Popen(
            subprocess_maybe_shell_wrap_exec(
                sys.executable,
                '-c',
                pyremote.pyremote_build_bootstrap_cmd('test'),
            ),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            env={
                **os.environ,
                'OMLISH_PYCHARM_RUNHACK_ENABLED': '0',
            },
        )

        stdin = check_not_none(proc.stdin)
        stdout = check_not_none(proc.stdout)

        res = pyremote.PyremoteBootstrapDriver(main_src).run(stdin, stdout)
        self.assertEqual(res.pid, proc.pid)

        stdin.write(b'foo')
        try:
            stdin.close()
        except BrokenPipeError:
            pass

        out = stdout.read()
        self.assertEqual(out, b'!foo!')
