import os.path
import subprocess

from omlish.docker import timebomb_payload
from omlish.testing.pydevd import silence_subprocess_check

USE_DOCKERFILE = True
TIMEBOMB_DELAY_S = 20 * 60


def _main():
    silence_subprocess_check()

    if USE_DOCKERFILE:
        img_name = 'wrmsr/omlish-piku-demo'
        cur_dir = os.path.dirname(__file__)
        subprocess.check_call([
            'docker', 'build',
            '--tag', img_name,
            '-f', os.path.join(cur_dir, 'Dockerfile'),
            cur_dir,
        ])

    else:
        img_name = 'ubuntu:22.04'

    ctr_id = subprocess.check_output([
        'docker', 'run',
        '-d',
        '-p', '9080:9080',
        img_name,
        'sleep', 'infinity',
    ]).decode().strip()
    print(f'{ctr_id=}')

    try:
        if TIMEBOMB_DELAY_S:
            subprocess.check_call([
                'docker', 'exec', '-id', ctr_id,
                'sh', '-c', timebomb_payload(TIMEBOMB_DELAY_S),
            ])

        def get(*args):
            subprocess.check_output(['docker', 'exec', '-i', ctr_id, *args])

        def do(*args):
            subprocess.check_call(['docker', 'exec', '-i', ctr_id, *args])

        def sh(*ss):
            do('sh', '-c', ' && '.join(ss))

        deps = [
            'curl',
            'dumb-init',
            'git',
            'nginx',
            'openssh-server',
            'openssl',
            'python3',
            'tmux',
            'vim',
            'wget',
        ]

        sh(
            'apt update',
            'DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y tzdata',
            f'DEBIAN_FRONTEND=noninteractive apt install -y {" ".join(deps)}',
        )

        sh(
            'cd ~',
            'curl https://piku.github.io/get | sh',
            './piku-bootstrap first-run --no-interactive',
            '(.piku-bootstrap/piku-bootstrap/piku-bootstrap install piku.yml || true)',
        )

        sh(
            'ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""',
            'cp ~/.ssh/id_rsa.pub /tmp/id_rsa.pub',
            'su - piku -c \'~piku/piku.py setup:ssh /tmp/id_rsa.pub\'',
        )

        sh(
            'service ssh start',
            'ssh -o StrictHostKeyChecking=accept-new piku@localhost',
        )

        sh(
            'service cron start',
            'echo \'\\ninclude /home/piku/.piku/nginx/*.conf;\\n\' >> /etc/nginx/sites-available/default',
            'service nginx start',
        )

        sh(
            'tmux new-session -d -s uwsgi-piku uwsgi-piku --ini ~piku/.piku/uwsgi/uwsgi.ini',
        )

        sh(
            'cd ~',
            'git config --global user.email "piku-demo@wrmsr.com"',
            'git config --global user.name "piku-demo"',
            'git clone https://github.com/piku/sample-python-app',
            'cd sample-python-app',
            'git remote add piku piku@localhost:sample_python_app',
            'git push piku master',
        )

        print()
        print(ctr_id)
        print()
        print('done - press enter to die')
        input()

    finally:
        subprocess.check_call(['docker', 'kill', '-sKILL', ctr_id])


if __name__ == '__main__':
    _main()
