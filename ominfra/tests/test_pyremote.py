# ruff: noqa: PT009
# @omlish-lite
import os.path
import subprocess
import sys
import unittest

from omlish.lite.check import check
from omlish.subprocesses.wrap import subprocess_maybe_shell_wrap_exec

from .. import pyremote


class TestPyremote(unittest.TestCase):
    def _run_test(self, opts: pyremote.PyremoteBootstrapOptions) -> None:
        with open(os.path.join(os.path.dirname(__file__), '..', 'pyremote.py')) as f:
            pyr_src = f.read()

        payload_src = '\n'.join([
            pyr_src,
            'rt = pyremote_bootstrap_finalize()',
            'b = rt.input.read()',
            'rt.output.write(b"!" + b + b"!")',
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
        )

        stdin = check.not_none(proc.stdin)
        stdout = check.not_none(proc.stdout)

        res = pyremote.PyremoteBootstrapDriver(
            payload_src,
            opts,
        ).run(stdout, stdin)
        self.assertEqual(res.pid, proc.pid)

        stdin.write(b'foo')
        try:
            stdin.close()
        except BrokenPipeError:
            pass

        out = stdout.read()
        self.assertEqual(out, b'!foo!')

    def test_normal(self) -> None:
        self._run_test(pyremote.PyremoteBootstrapOptions())

    def test_debug(self) -> None:
        self._run_test(pyremote.PyremoteBootstrapOptions(debug=True))
