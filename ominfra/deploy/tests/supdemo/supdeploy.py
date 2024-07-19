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
"""  # noqa
import functools
import logging
import os.path
import pwd
import shlex
import subprocess
import sys
import typing as ta


T = ta.TypeVar('T')


REQUIRED_PYTHON_VERSION = (3, 8)


log = logging.getLogger(__name__)


##


def _check_not_none(v: ta.Optional[T]) -> T:
    if v is None:
        raise ValueError
    return v


def _check_not(v: ta.Any) -> None:
    if v:
        raise ValueError(v)
    return v


class cached_nullary:  # noqa
    def __init__(self, fn):
        self._fn = fn
        self._value = self._missing = object()
        functools.update_wrapper(self, fn)
    def __call__(self, *args, **kwargs):  # noqa
        if self._value is self._missing:
            self._value = self._fn()
        return self._value
    def __get__(self, instance, owner):  # noqa
        bound = instance.__dict__[self._fn.__name__] = self.__class__(self._fn.__get__(instance, owner))
        return bound


def _mask_env_kwarg(kwargs):
    return {**kwargs, **({'env': '...'} if 'env' in kwargs else {})}


def _subprocess_check_call(*args, stdout=sys.stderr, **kwargs):
    log.debug((args, _mask_env_kwarg(kwargs)))
    return subprocess.check_call(*args, stdout=stdout, **kwargs)  # type: ignore


def _subprocess_check_output(*args, **kwargs):
    log.debug((args, _mask_env_kwarg(kwargs)))
    return subprocess.check_output(*args, **kwargs)


##


PYTHON_BIN = 'python3.12'
USERNAME = 'deploy'
APP_NAME = 'omlish'
REPO_URL = 'https://github.com/wrmsr/omlish'
REVISION = 'cb60a99124c4d6973ac6e88d1a4313bcc9d8a197'
REQUIREMENTS_TXT = 'requirements.txt'
ENTRYPOINT = 'omserv.server.tests.hello'

GLOBAL_SUPERVISOR_CONF_PATH = '/etc/supervisor/conf.d/supervisord.conf'
GLOBAL_NGINX_CONF_PATH = '/etc/nginx/sites-enabled/deploy.conf'


def sh(*ss):
    s = ' && '.join(ss)
    log.info('Executing: %s', s)
    _subprocess_check_call(s, shell=True)


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

    ###

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

    ##

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

    ##

    nginx_conf_dir = os.path.join(home_dir, 'conf/nginx')
    if not os.path.isfile(GLOBAL_NGINX_CONF_PATH):
        log.info('Writing global nginx conf at %s', GLOBAL_NGINX_CONF_PATH)
        with open(GLOBAL_NGINX_CONF_PATH, 'w') as f:
            f.write(f'include {nginx_conf_dir}/*.conf;\n')

    log.info('Starting nginx')
    sh('service nginx start')

    ##

    sup_conf_dir = os.path.join(home_dir, 'conf/supervisor')
    with open(GLOBAL_SUPERVISOR_CONF_PATH, 'r') as f:
        glo_sup_conf = f.read()
    if sup_conf_dir not in glo_sup_conf:
        log.info('Updating global supervisor conf at %s', GLOBAL_SUPERVISOR_CONF_PATH)
        glo_sup_conf += f"""
[include]
files = {home_dir}/conf/supervisor/*.conf
"""
        with open(GLOBAL_SUPERVISOR_CONF_PATH, 'w') as f:
            f.write(glo_sup_conf)

    ###

    clone_submodules = False
    ush(
        'cd ~/app',
        f'git clone --depth 1 {REPO_URL} {APP_NAME}',
        *([
            f'cd {APP_NAME}',
            'git submodule update --init',
        ] if clone_submodules else []),
    )

    ##

    ush(
        'cd ~/venv',
        f'{PYTHON_BIN} -mvenv {APP_NAME}',
        f'{APP_NAME}/bin/python -mpip install -r ~deploy/app/{APP_NAME}/{REQUIREMENTS_TXT}',
    )

    ##

    nginx_conf = f"""
server {{
    listen 80;
    location / {{
        proxy_pass http://127.0.0.1:8000/;
    }}
}}
"""  # noqa
    nginx_conf_file = os.path.join(home_dir, f'conf/nginx/{APP_NAME}.conf')
    log.info('Writing nginx conf to %s', nginx_conf_file)
    with open(nginx_conf_file, 'w') as f:
        f.write(nginx_conf)

    ##

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

    log.info('Poking supervisor')
    sh('kill -HUP 1')

    ##

    log.info('Poking nginx')
    sh('nginx -s reload')

    ##

    log.info('Shitty deploy complete!')


if __name__ == '__main__':
    _main()
