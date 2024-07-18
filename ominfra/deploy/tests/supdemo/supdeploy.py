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
import subprocess


def sh(*ss):
    subprocess.check_call(' && '.join(ss), shell=True)


def _main() -> None:
    print('hi from supdeploy')
    sh('hostname')


if __name__ == '__main__':
    _main()
