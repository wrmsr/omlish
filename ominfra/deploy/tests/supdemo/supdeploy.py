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
import subprocess
import sys


REQUIRED_PYTHON_VERSION = (3, 8)


log = logging.getLogger(__name__)


USERNAME = 'deploy'


def sh(*ss):
    subprocess.check_call(' && '.join(ss), shell=True)


def _main() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

    if sys.platform != 'linux':
        raise EnvironmentError('must run on linux')

    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')

    try:
        pwd.getpwnam(USERNAME)
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

    home_dir = os.path.expanduser(f'~{USERNAME}')
    for dn in [
        'app',
        'conf',
        'conf/env',
        'conf/nginx',
        'conf/supervisor',
        'conf/supervisor',
        'venv',
    ]:
        fp = os.path.join(home_dir, dn)
        if not os.path.exists(fp):
            log.info('Creating directory: %s', fp)


if __name__ == '__main__':
    _main()
