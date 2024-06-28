"""
TODO:
 - just use a Dockerfile lol

--

ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""
cp ~/.ssh/id_rsa.pub /tmp/id_rsa.pub
su - piku -c '~piku/piku.py setup:ssh /tmp/id_rsa.pub'

service ssh start
ssh -o StrictHostKeyChecking=accept-new piku@localhost

git clone https://github.com/piku/sample-python-app
cd sample-python-app
git remote add piku piku@localhost:sample_python_app
git push piku master

uwsgi-piku --ini ~piku/.piku/uwsgi/uwsgi.ini &

curl localhost:9080
"""
import subprocess
import time


def _main():
    ctr_id = subprocess.check_output(['docker', 'run', '-d', 'ubuntu', 'sleep', 'infinity']).decode().strip()
    print(f'{ctr_id=}')

    try:
        def get(*args):
            subprocess.check_output(['docker', 'exec', '-i', ctr_id, *args])

        def do(*args):
            subprocess.check_call(['docker', 'exec', '-i', ctr_id, *args])

        def sh(s):
            do('sh', '-c', s)

        sh(
            'apt update && '
            'DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y tzdata && '
            'apt install -y python3 git nginx curl openssl wget vim tmux openssh-server'
        )

        sh(
            'cd ~ && '
            'curl https://piku.github.io/get | sh && '
            './piku-bootstrap first-run --no-interactive && '
            '.piku-bootstrap/piku-bootstrap/piku-bootstrap install piku.yml'
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
