"""
~omlish
  deploy.pid (flock)
  /conf
    /env
      wrmsr--omlish--<spec>.env
    /nginx
      wrmsr--omlish--<spec>.conf
    /supervisor
      wrmsr--omlish--<spec>.conf
  /venv
    /wrmsr--omlish--<spec>

?
  /logs
    /wrmsr--omlish--<spec>

spec = <rev>--<when>

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

"""
import subprocess


def sh(*ss):
    subprocess.check_call(' && '.join(ss), shell=True)


def _main() -> None:
    print('hi from supdeploy')
    sh('hostname')


if __name__ == '__main__':
    _main()
