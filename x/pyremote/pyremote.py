import base64
import inspect
import os
import socket
import subprocess
import sys
import typing as ta
import zlib


class Connection:
    def __init__(self, proc: subprocess.Popen) -> None:
        super().__init__()
        self._proc = proc


def _bootstrap_main(context_name: str, main_z_len: int) -> None:
    r, w = os.pipe()

    if os.fork():
        os.dup2(0, 100)
        os.dup2(r, 0)

        os.close(r)
        os.close(w)

        os.environ['ARGV0'] = sys.executable
        os.execl(sys.executable, sys.executable + f'(pyremote:{context_name})')

    os.write(1, b'OPYR000\n')

    main_src = zlib.decompress(os.fdopen(0, 'rb').read(main_z_len))

    fp = os.fdopen(w, 'wb', 0)
    fp.write(main_src)
    fp.close()

    os.write(1, b'OPYR001\n')
    os.close(2)


def _bootstrap_payload(context_name: str, main_z_len: int) -> str:
    bs_main_src = inspect.getsource(_bootstrap_main)
    bs_main_z = zlib.compress(bs_main_src.encode('utf-8'))

    bs_main_z64 = base64.encodebytes(bs_main_z).decode('utf-8').replace('\n', '').encode('utf-8')
    bs_stmts = [
        'import base64, os, sys, zlib',
        f'exec(zlib.decompress(base64.decodebytes({bs_main_z64!r})))',
        f'_bootstrap_main({context_name!r}, {main_z_len})'
    ]
    bs_cmd = '; '.join(bs_stmts)
    return bs_cmd


T = ta.TypeVar('T')


def _check_eq(l: T, r: T) -> T:
    if l != r:
        raise Exception(f'Must be equal: {l}, {r}')
    return l


def _connect_docker(ctr_id: str) -> Connection:
    context_name = f'docker:{ctr_id}'

    real_main_src = inspect.getsource(sys.modules[__name__])
    main_src = '\n'.join([
        '__name__ = "__pyremote_child_main__"\n',
        real_main_src,
        '\n_child_main()\n',
    ])
    main_z = zlib.compress(main_src.encode('utf-8'))

    proc = subprocess.Popen(
        [
            'docker', 'exec', '-i', ctr_id,
            'python3', '-c', _bootstrap_payload(context_name, len(main_z)),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    proc.stdin.write(main_z)
    proc.stdin.flush()

    _check_eq(proc.stdout.read(8), b'OPYR000\n')
    _check_eq(proc.stdout.read(8), b'OPYR001\n')

    conn = Connection(
        proc,
    )
    return conn


def _child_main() -> None:
    print(f'hi from child: {socket.gethostname()}', file=sys.stderr)


TIMEBOMB_DELAY_S = 20 * 60


def _main() -> None:
    from omlish.docker import timebomb_payload
    from omlish.testing.pydevd import silence_subprocess_check

    silence_subprocess_check()

    img_name = 'python:3.8'

    ctr_id = subprocess.check_output([
        'docker', 'run', '-d', img_name,
        'sleep', 'infinity',
    ]).decode().strip()
    print(f'{ctr_id=}')

    try:
        if TIMEBOMB_DELAY_S:
            subprocess.check_call([
                'docker', 'exec', '-id', ctr_id,
                'sh', '-c', timebomb_payload(TIMEBOMB_DELAY_S),
            ])

        conn = _connect_docker(ctr_id)

        print(conn._proc.stderr.read())

        print()
        print(ctr_id)
        print()
        print('done - press enter to die')
        input()

    finally:
        subprocess.check_call(['docker', 'kill', '-sKILL', ctr_id])


if __name__ == '__main__':
    _main()
