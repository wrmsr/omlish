import json
import os.path
import subprocess
import textwrap
import traceback

from omlish.docker import timebomb_payload
from omlish.testing.pydevd import silence_subprocess_check


TIMEBOMB_DELAY_S = 20 * 60

SCRIPT_TEMP_FILE = False
PYCHARM_DEBUG = False


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

        with open(os.path.join(os.path.dirname(__file__), 'scripts/supdeploy.py')) as f:
            buf = f.read()

        if PYCHARM_DEBUG:
            pycharm_port = 43251
            pycharm_version = '241.18034.82'
            buf = textwrap.dedent(f"""
                import subprocess
                import sys
                subprocess.check_call([sys.executable, '-mpip', 'install', f'pydevd-pycharm~={pycharm_version}'])

                import pydevd_pycharm  # noqa
                pydevd_pycharm.settrace(
                    'docker.for.mac.localhost',
                    port={pycharm_port},
                    stdoutToServer=True,
                    stderrToServer=True,
                )
            """) + '\n' * 2 + buf

        cfg = dict(
            python_bin='python3.12',
            app_name='omlish',
            repo_url='https://github.com/wrmsr/omlish',
            revision='d2002c719fcba45d30b9d0e288f317478315f534',
            requirements_txt='requirements.txt',
            entrypoint='omserv.server.tests.hello',
        )

        if SCRIPT_TEMP_FILE:
            subprocess.run([
                'docker', 'exec', '-i', ctr_id,
                'sh', '-c', f'cp /dev/stdin {fname}',
            ], input=buf.encode(), check=True)

            subprocess.check_call([
                'docker', 'exec', '-i', ctr_id,
                'python3', fname, 'deploy', json.dumps(cfg),
            ])

        else:
            subprocess.run([
                'docker', 'exec', '-i', ctr_id,
                'python3', '-', 'deploy', json.dumps(cfg),
            ], input=buf.encode(), check=True)

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
        subprocess.check_call(['docker', 'kill', '-sKILL', ctr_id])


if __name__ == '__main__':
    _main()
