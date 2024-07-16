"""
https://docs.docker.com/config/containers/multi-service_container/#use-a-process-manager
https://serverfault.com/questions/211525/supervisor-not-loading-new-configuration-files
"""
import os.path
import subprocess

from omlish.docker import timebomb_payload
from omlish.testing.pydevd import silence_subprocess_check


TIMEBOMB_DELAY_S = 20 * 60


def _main():
    silence_subprocess_check()

    img_name = 'wrmsr/omlish-sup-demo'
    cur_dir = os.path.dirname(__file__)
    subprocess.check_call([
        'docker', 'build',
        '--tag', img_name,
        '-f', os.path.join(cur_dir, 'Dockerfile'),
        cur_dir,
    ])

    ctr_id = subprocess.check_output([
        'docker', 'run', '-d', img_name,
    ]).decode().strip()
    print(f'{ctr_id=}')

    try:
        if TIMEBOMB_DELAY_S:
            subprocess.check_call([
                'docker', 'exec', '-id', ctr_id,
                'sh', '-c', timebomb_payload(TIMEBOMB_DELAY_S),
            ])

            subprocess.check_call([
                'docker', 'exec', ctr_id,
                'python3.12', '--version',
            ])

            print()
            print(ctr_id)
            print()
            print('done - press enter to die')
            input()

    finally:
        subprocess.check_call(['docker', 'kill', '-sKILL', ctr_id])


if __name__ == '__main__':
    _main()
