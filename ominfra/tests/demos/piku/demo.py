import os.path
import subprocess

from .. import utils as u


USE_DOCKERFILE = True
TIMEBOMB_DELAY_S = 20 * 60


def _main() -> None:
    if USE_DOCKERFILE:
        img_name = 'wrmsr/omlish-piku-demo'
        cur_dir = os.path.dirname(__file__)
        u.build_docker_image(img_name, cur_dir)

    else:
        img_name = 'ubuntu:22.04'

    with u.launch_docker_container(
            '-p', '9080:9080',
            img_name,
            'sleep', 'infinity',
            timebomb_delay_s=TIMEBOMB_DELAY_S,
    ) as ctr_id:
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


if __name__ == '__main__':
    _main()
