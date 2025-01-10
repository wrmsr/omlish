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
    if not shutil.which('clang++'):
        pytest.skip('no clang++')

    stub_src = f"""\
#!/usr/bin/env sh
[ "$1" = "cc" ] || exit 1 ; shift
exec {shlex.quote(os.path.abspath(sys.executable))} -m omdev.cc "$@"
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
        os.path.join(os.path.dirname(__file__), 'hi.cc'),
        'foo bar',
        'baz',
    )
    lines = out.decode().splitlines()  # noqa

    assert len(lines) == 4
    assert lines[0] == 'Arguments (3):'
    assert lines[1].endswith('hi.cc')
    assert lines[2] == 'argv[1]: foo bar'
    assert lines[3] == 'argv[2]: baz'


@pytest.mark.online
def test_json(tmpdir):
    out = _compile_and_run(
        str(tmpdir),
        os.path.join(os.path.dirname(__file__), 'json.cc'),
    )

    assert out.decode().strip() == (
        '{"answer":{"everything":42},"happy":true,"list":[1,0,2],"name":"Niels","nothing":null,"object":{"currency":"USD","value":42.99},"pi":3.141}'  # noqa
    )
