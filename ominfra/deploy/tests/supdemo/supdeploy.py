"""
~omlish
  /conf
    /nginx
      wrmsr--omlish--<rev>.conf
    /supervisor
      wrmsr--omlish--<rev>.conf
  /venv
    /wrmsr--omlish--<rev>--deploy

https://docs.docker.com/config/containers/multi-service_container/#use-a-process-manager
https://serverfault.com/questions/211525/supervisor-not-loading-new-configuration-files

adduser \
  --system \
  --disabled-password \
  --group \
  --shell /bin/bash \
  omlish
"""


def _main() -> None:
    print('hi from supdeploy')


if __name__ == '__main__':
    _main()
