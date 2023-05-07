import os.path
import subprocess
import sys

from .. import bootstrap  # noqa


TEST_SRC = f"""
from {__package__.split('.')[0]} import bootstrap
with bootstrap.Bootstrap() as bs:
    print(bs)
"""


def test_bootstrap(tmpdir):
    fp = os.path.join(tmpdir, 'test_bootstrap.py')
    with open(fp, 'w') as f:
        f.write(TEST_SRC)
    pp = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    if 'PYTHONPATH' in os.environ:
        pp += os.pathsep + os.environ['PYTHONPATH']
    subprocess.check_call(
        [sys.executable, fp],
        env={**os.environ, 'PYTHONPATH': pp},
    )
