import os.path
import shlex
import shutil
import subprocess
import sys

import pytest

from omlish import check


def _compile_and_run(
        tmp_dir: str,
        src_file: str,
        *args: str,
) -> bytes:
    if not shutil.which('java'):
        pytest.skip('no java')

    stub_src = f"""\
#!/usr/bin/env sh
[ "$1" = "java" ] || exit 1 ; shift
exec {shlex.quote(os.path.abspath(sys.executable))} -m omdev.java "$@"
"""

    with open((om_stub := os.path.join(tmp_dir, 'om')), 'w') as f:
        f.write(stub_src)
    os.chmod(om_stub, 0o700)

    out = subprocess.check_output(
        [
            check.non_empty_str(shutil.which('sh')),
            src_file,
            *args,
        ],
        env={
            **os.environ,
            'PATH': os.path.pathsep.join([tmp_dir, os.environ.get('PATH', '')]),
        },
    )

    return out


def test_hi(tmpdir):
    out = _compile_and_run(
        str(tmpdir),
        os.path.join(os.path.dirname(__file__), 'src/Hi.java'),
        'foo bar',
        'baz',
    )
    lines = out.decode().splitlines()  # noqa

    assert len(lines) == 3
    assert lines[0] == 'Arguments (2):'
    assert lines[1] == 'argv[0]: foo bar'
    assert lines[2] == 'argv[1]: baz'


def test_hi_deps(tmpdir):
    out = _compile_and_run(
        str(tmpdir),
        os.path.join(os.path.dirname(__file__), 'src/HiDeps.java'),
        'foo bar',
        'baz',
    )
    lines = out.decode().splitlines()  # noqa

    assert len(lines) == 3
    assert lines[0] == 'Arguments (2):'
    assert lines[1] == 'argv[0]: foo bar'
    assert lines[2] == 'argv[1]: baz'
