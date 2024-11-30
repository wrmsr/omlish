# @omlish-lite
import os.path
import subprocess
import sys
import unittest

from .. import pyremote


class TestPyremote(unittest.TestCase):
    def test_pyremote(self):
        with open(os.path.join(os.path.dirname(__file__), '..', 'pyremote.py')) as f:
            pyr_src = f.read()

        main_src = '\n'.join([
            pyr_src,
            'pyremote_bootstrap_finalize()',
            'os.write(1, "hi")',
        ])

        proc = subprocess.Popen([
            sys.exec_prefix,
            pyremote.pyremote_build_bootstrap_cmd('test'),
        ])
