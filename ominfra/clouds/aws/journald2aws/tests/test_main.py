import json
import os
import subprocess
import sys
import tempfile


def mkstemp() -> str:
    fd, fn = tempfile.mkstemp()
    os.close(fd)
    os.unlink(fn)
    return fn


def test_main():
    config = dict(
        pid_file=(pid_file := mkstemp()),
        cursor_file=(cursor_file := mkstemp()),
        runtime_limit=5.,
        aws_log_stream_name='foo',
    )

    with open(cfg_file := mkstemp(), 'w') as f:
        f.write(json.dumps(config))

    proc = subprocess.Popen([
        sys.executable,
        '-m',
        __package__.rpartition('.')[0] + '.main',
        '--config-file', cfg_file,
        '--dry-run',
        '--verbose',
        # '--num-messages', '10',
    ])
    proc.communicate()
    assert not proc.returncode

    with open(pid_file) as f:
        pid = f.read()
    with open(cursor_file) as f:
        cursor = f.read()

    print(pid)
    print(cursor)
