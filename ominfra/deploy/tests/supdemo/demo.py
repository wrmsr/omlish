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
        'docker', 'run',
        '-d',
        '-p', '9322:22',
        '-p', '9380:80',
        '-p', '9343:443',
        img_name,
    ]).decode().strip()
    print(f'{ctr_id=}')

    try:
        if TIMEBOMB_DELAY_S:
            subprocess.check_call([
                'docker', 'exec', '-id', ctr_id,
                'sh', '-c', timebomb_payload(TIMEBOMB_DELAY_S),
            ])

            fname = subprocess.check_output([
                'docker', 'exec', ctr_id,
                'mktemp', '--suffix=-supdeploy',
            ]).decode().strip()

            with open(os.path.join(os.path.dirname(__file__), 'supdeploy.py'), 'rb') as f:
                buf = f.read()

            subprocess.run([
                'docker', 'exec', '-i', ctr_id,
                'sh', '-c', f'cp /dev/stdin {fname}',
            ], input=buf, check=True)

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            # RUN ( \
            #     python3.12 -m ensurepip --upgrade && \
            #     python3.12 -m pip install --upgrade setuptools \
            # )

            subprocess.check_call([
                'docker', 'exec', '-i', ctr_id,
                'python3.12', fname,
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
