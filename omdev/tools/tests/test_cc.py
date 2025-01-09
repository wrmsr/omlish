import os.path
import shutil
import subprocess
import sys

import pytest

from omlish import check


def test_cc_run(tmpdir):
    tmp_dir = str(tmpdir)

    stub_src = f"""\
#!/usr/bin/env sh
[ "$1" = "cc" ] || exit 1 ; shift
exec {os.path.abspath(sys.executable)} -m omdev.tools.cc "$@"
"""

    if not shutil.which('clang++'):
        pytest.skip('no clang++')

    with open((om_stub := os.path.join(tmp_dir, 'om')), 'w') as f:
        f.write(stub_src)
    os.chmod(om_stub, 0o700)

    test_dir = os.path.abspath(os.path.dirname(__file__))
    src_file = os.path.join(test_dir, 'hi.cc')

    out = subprocess.check_output(
        [
            check.non_empty_str(shutil.which('sh')),
            src_file,
            'foo bar',
            'baz',
        ],
        env={
            **os.environ,
            'PATH': os.path.pathsep.join([tmp_dir, os.environ.get('PATH', '')]),
        },
    ).decode()

    lines = out.splitlines()  # noqa

    assert len(lines) == 4
    assert lines[0] == 'Arguments (3):'
    assert lines[1].endswith('hi.cc')
    assert lines[2] == 'argv[1]: foo bar'
    assert lines[3] == 'argv[2]: baz'
