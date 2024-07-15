import base64
import inspect
import os
import subprocess
import sys
import typing as ta
import zlib


class Connection:
    def __init__(self, proc: subprocess.Popen) -> None:
        super().__init__()
        self._proc = proc


def _bootstrap_main(context_name: str, main_compressed_len: int) -> None:
    r, w = os.pipe()

    if os.fork():
        os.dup2(0, 100)
        os.dup2(r, 0)

        os.close(r)
        os.close(w)

        os.environ['ARGV0'] = sys.executable
        os.execl(sys.executable, sys.executable + f'(pyremote:{context_name})')

    os.write(1, 'OPRO000\n'.encode())

    main_src = zlib.decompress(os.fdopen(0, 'rb').read(main_compressed_len))

    fp = os.fdopen(w, 'wb', 0)
    fp.write(main_src)
    fp.close()

    os.write(1, 'OPRO001\n'.encode())
    os.close(2)


def _bootstrap_payload(context_name: str) -> str:
    main_compressed_len = 420

    bs_main_src = inspect.getsource(_bootstrap_main)
    bs_main_z = zlib.compress(bs_main_src.encode('utf-8'))
    bs_main_z64 = base64.encodebytes(bs_main_z).decode('utf-8').replace('\n', '').encode('utf-8')
    bs_stmts = [
        'import base64, os, sys, zlib',
        f'exec(zlib.decompress(base64.decodebytes({bs_main_z64!r})))',
        f'_bootstrap_main({context_name!r}, {main_compressed_len})'
    ]
    bs_cmd = '; '.join(bs_stmts)
    return bs_cmd


def _connect_docker(ctr_id: str) -> Connection:
    context_name = f'docker:{ctr_id}'

    proc = subprocess.Popen(
        [
            'docker',
            'exec',
            '-i',
            ctr_id,
            'python3',
            '-c',
            _bootstrap_payload(context_name),
        ],
    )
    return Connection(
        proc,
    )


TIMEBOMB_DELAY_S = 20 * 60


def _main():
    from omlish.docker import timebomb_payload
    from omlish.testing.pydevd import silence_subprocess_check

    silence_subprocess_check()

    img_name = 'python:3.8'

    ctr_id = subprocess.check_output([
        'docker', 'run',
        '-d',
        img_name,
        'sleep', 'infinity',
    ]).decode().strip()
    print(f'{ctr_id=}')

    try:
        if TIMEBOMB_DELAY_S:
            subprocess.check_call([
                'docker', 'exec',
                '-id', ctr_id,
                'sh', '-c',
                timebomb_payload(TIMEBOMB_DELAY_S),
            ])

        conn = _connect_docker(ctr_id)

        print()
        print(ctr_id)
        print()
        print('done - press enter to die')
        input()

    finally:
        subprocess.check_call(['docker', 'kill', '-sKILL', ctr_id])

if __name__ == '__main__':
    _main()
