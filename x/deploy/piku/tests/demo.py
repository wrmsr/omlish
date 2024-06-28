import os.path
import subprocess
import time


USE_DOCKERFILE = True


def _main():
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
        'sleep', 'infinity'
    ]).decode().strip()
    print(f'{ctr_id=}')

    try:
        def get(*args):
            subprocess.check_output(['docker', 'exec', '-i', ctr_id, *args])

        def do(*args):
            subprocess.check_call(['docker', 'exec', '-i', ctr_id, *args])

        def sh(s):
            do('sh', '-c', s)

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

        if not USE_DOCKERFILE:
            sh('apt update')

        sh(
            'DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y tzdata && '
            f'DEBIAN_FRONTEND=noninteractive apt install -y {" ".join(deps)}'
        )

        sh(
            'cd ~ && '
            'curl https://piku.github.io/get | sh && '
            './piku-bootstrap first-run --no-interactive && '
            '(.piku-bootstrap/piku-bootstrap/piku-bootstrap install piku.yml || true)'
        )

        sh(
            'ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N "" && '
            'cp ~/.ssh/id_rsa.pub /tmp/id_rsa.pub && '
            'su - piku -c \'~piku/piku.py setup:ssh /tmp/id_rsa.pub\''
        )

        sh(
            'service ssh start && '
            'ssh -o StrictHostKeyChecking=accept-new piku@localhost'
        )

        sh(
            'service nginx start'
        )

        sh(
            'tmux new-session -d -s uwsgi-piku uwsgi-piku --ini ~piku/.piku/uwsgi/uwsgi.ini'
        )

        sh(
            'git clone https://github.com/piku/sample-python-app && '
            'cd sample-python-app && '
            'git remote add piku piku@localhost:sample_python_app && '
            'git push piku master'
        )

        print('done')
        time.sleep(10)

    finally:
        subprocess.check_call(['docker', 'kill', '-sKILL', ctr_id])


if __name__ == '__main__':
    _main()
