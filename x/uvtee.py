"""
https://docs.python.org/3/library/pty.html

Alt?: https://gist.github.com/scivision/3629a57ea6f78c1450f2b8d4e81b8a4b
"""
import io
import os
import pty
import re
import shutil
import subprocess


##
# https://stackoverflow.com/a/14693789


_ANSI_ESCAPE_PAT = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def strip_ansi_escapes_str(s: str) -> str:
    return _ANSI_ESCAPE_PAT.sub('', s)


_ANSI_ESCAPE_8BIT_PAT = re.compile(br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])')


def strip_ansi_escapes_bytes(b: bytes) -> bytes:
    return _ANSI_ESCAPE_8BIT_PAT.sub(b'', b)


##


def _main() -> None:
    buf = io.BytesIO()

    def read(fd: int) -> bytes:
        data = os.read(fd, 0x4000)
        buf.write(data)
        return data

    cmds = [
        'rm -rf .venv-install || true',
        '~/.pyenv/versions/3.12.6/bin/python -mvenv .venv-install',
        '. .venv-install/bin/activate',
        'pip install uv',
        'uv pip install -r requirements-dev.txt',
    ]
    pty.spawn([shutil.which('sh'), '-c', ' && '.join(cmds)], read)

    out = strip_ansi_escapes_bytes(buf.getvalue())
    lines = out.split(b'\r\n')

    print('\n'.join(map(repr, lines)))

    subprocess.run('rm -rf .venv-install', shell=True)


if __name__ == '__main__':
    _main()
