"""
~deploy
  deploy.pid (flock)
  /app
    /<appspec> - shallow clone
  /conf
    /env
      <appspec>.env
    /nginx
      <appspec>.conf
    /supervisor
      <appspec>.conf
  /venv
    /<appspec>

?
  /logs
    /wrmsr--omlish--<spec>

spec = <name>--<rev>--<when>

https://docs.docker.com/config/containers/multi-service_container/#use-a-process-manager
https://serverfault.com/questions/211525/supervisor-not-loading-new-configuration-files

adduser \
  --system \
  --disabled-password \
  --group \
  --shell /bin/bash \
  omlish

==

~piku/.piku
  /apps/<app>
  /data/<app>
  /envs/<app>
  /logs/<app>
  /nginx
  /repos/<app>
  /uwsgi
  /uwsgi-available/<app>_<proc>.<n>.ini

==

[program:myapp_live]
command=/usr/local/bin/gunicorn_django --log-file /home/myapp/logs/gunicorn_live.log --log-level info --workers 2 -t 120 -b 127.0.0.1:10000 -p deploy/gunicorn_live.pid webapp/settings_live.py
directory=/home/myapp/live
environment=PYTHONPATH='/home/myapp/live/eco/lib'
user=myapp
autostart=true
autorestart=true
"""  # noqa
import logging
import os.path
import pwd
import shlex
import subprocess
import sys


REQUIRED_PYTHON_VERSION = (3, 8)


log = logging.getLogger(__name__)


USERNAME = 'deploy'
APP_NAME = 'omlish'
REPO_URL = 'https://github.com/wrmsr/omlish'
REVISION = 'cb60a99124c4d6973ac6e88d1a4313bcc9d8a197'
REQUIREMENTS_TXT = 'requirements-dev.txt'
ENTRYPOINT = 'omserv.server.tests.hello'


def sh(*ss):
    s = ' && '.join(ss)
    log.info('Executing: %s', s)
    subprocess.check_call(s, shell=True)


def ush(*ss):
    s = ' && '.join(ss)
    sh(f"su - {USERNAME} -c {shlex.quote(s)}")


def _main() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

    if sys.platform != 'linux':
        raise EnvironmentError('must run on linux')
    True  # type: ignore  # noqa

    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')

    try:
        pwn = pwd.getpwnam(USERNAME)
    except KeyError:
        log.info('Creating user %s', USERNAME)
        sh(' '.join([
            'adduser',
            '--system',
            '--disabled-password',
            '--group',
            '--shell /bin/bash',
            USERNAME,
        ]))
        pwn = pwd.getpwnam(USERNAME)

    home_dir = os.path.expanduser(f'~{USERNAME}')
    for dn in [
        'app',
        'conf',
        'conf/env',
        'conf/nginx',
        'conf/supervisor',
        'venv',
    ]:
        fp = os.path.join(home_dir, dn)
        if not os.path.exists(fp):
            log.info('Creating directory: %s', fp)
            os.mkdir(fp)
            os.chown(fp, pwn.pw_uid, pwn.pw_gid)

    clone_submodules = False
    ush(
        'cd ~/app',
        f'git clone --depth 1 {REPO_URL} {APP_NAME}',
        *([
            f'cd {APP_NAME}',
            'git submodule update --init',
        ] if clone_submodules else []),
    )

    ush(
        'cd ~/venv',
        f'python3 -mvenv {APP_NAME}',
        f'{APP_NAME}/bin/python -mpip install -r ~deploy/app/{APP_NAME}/{REQUIREMENTS_TXT}',
    )

    sup_conf = f"""
[program:{APP_NAME}]
command={home_dir}/venv/{APP_NAME}/bin/python -m {ENTRYPOINT}
directory={home_dir}/app/{APP_NAME}
user={USERNAME}
autostart=true
autorestart=true
"""
    sup_conf_file = os.path.join(home_dir, f'conf/supervisor/{APP_NAME}.conf')
    log.info('Writing supervisor conf to %s', sup_conf_file)
    with open(sup_conf_file, 'w') as f:
        f.write(sup_conf)


if __name__ == '__main__':
    _main()
