import contextlib
import os.path
import subprocess
import traceback
import typing as ta

from omlish.diag.pydevd import silence_subprocess_check
from omlish.docker.timebomb import timebomb_payload


def run(*args, **kwargs):
    silence_subprocess_check()
    return subprocess.run(*args, **kwargs)  # noqa


def check_call(*args, **kwargs):
    silence_subprocess_check()
    return subprocess.check_call(*args, **kwargs)


def check_output(*args, **kwargs):
    silence_subprocess_check()
    return subprocess.check_output(*args, **kwargs)


def build_docker_image(img_name: str, cur_dir: str, dockerfile: str | None = None) -> None:
    check_call([
        'docker', 'build',
        '--tag', img_name,
        '-f', dockerfile if dockerfile is not None else os.path.join(cur_dir, 'Dockerfile'),
        cur_dir,
    ])


@contextlib.contextmanager
def launch_docker_container(
        *args: str,
        timebomb_delay_s: float | None = None,
) -> ta.Iterator[str]:
    ctr_id = check_output([
        'docker', 'run',
        '-d',
        *args,
    ]).decode().strip()

    try:
        print(ctr_id)
        print()

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
