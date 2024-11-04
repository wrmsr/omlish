import json
import os
import subprocess
import sys
import tempfile


def test_main():
    config = dict(
        aws_log_stream_name='foo',
        verbose=True,
    )

    fd, fn = tempfile.mkstemp()
    os.close(fd)

    with open(fn, 'w') as f:
        f.write(json.dumps(config))

    subprocess.check_call([
        sys.executable,
        '-m',
        __package__.rpartition('.')[0] + '.main',
        '--config-file', fn,
        '--dry-run',
    ])
