import contextlib
import os.path
import subprocess
import textwrap
import traceback
import typing as ta

from omlish.docker import timebomb_payload
from omlish.testing.pydevd import silence_subprocess_check


def run(*args, **kwargs):
    silence_subprocess_check()
    return subprocess.run(*args, **kwargs)


def check_call(*args, **kwargs):
    silence_subprocess_check()
    return subprocess.check_call(*args, **kwargs)


def check_output(*args, **kwargs):
    silence_subprocess_check()
    return subprocess.check_output(*args, **kwargs)


def build_docker_image(img_name: str, cur_dir: str) -> None:
    check_call([
        'docker', 'build',
        '--tag', img_name,
        '-f', os.path.join(cur_dir, 'Dockerfile'),
        cur_dir,
    ])


@contextlib.contextmanager
def launch_docker_container(
        img_name: str,
        *args: str,
        timebomb_delay_s: float | None = None,
) -> ta.Iterator[str]:
    ctr_id = check_output([
        'docker', 'run',
        '-d',
        *args,
        img_name,
    ]).decode().strip()

    try:
        if timebomb_delay_s:
            subprocess.check_call([
                'docker', 'exec', '-id', ctr_id,
                'sh', '-c', timebomb_payload(timebomb_delay_s),
            ])

        yield ctr_id

        print()
        print(ctr_id)
        print()
        print('done - press enter to die')
        input()

    except Exception:  # noqa
        traceback.print_exc()

        print()
        print(ctr_id)
        print()
        print('failed - press enter to die')
        input()

    finally:
        check_call(['docker', 'kill', '-sKILL', ctr_id])


def write_docker_temp_file(ctr_id: str, data: bytes, suffix: str = 'omlish') -> str:
    fname = check_output([
        'docker', 'exec', ctr_id,
        'mktemp', f'--suffix=-{suffix}',
    ]).decode().strip()

    run([
        'docker', 'exec', '-i', ctr_id,
        'sh', '-c', f'cp /dev/stdin {fname}',
    ], input=data, check=True)

    return fname


def pycharm_debug_preamble(port: int, version: str = '241.18034.82') -> str:
    return textwrap.dedent(f"""
        import subprocess
        import sys
        subprocess.check_call([sys.executable, '-mpip', 'install', f'pydevd-pycharm~={version}'])

        import pydevd_pycharm  # noqa
        pydevd_pycharm.settrace(
            'docker.for.mac.localhost',
            port={port},
            stdoutToServer=True,
            stderrToServer=True,
        )
    """)
