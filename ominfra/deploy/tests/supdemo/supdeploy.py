"""
TODO:
 - flock
 - interp.py

==

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
import dataclasses as dc
import functools
import logging
import os.path
import pwd
import shlex
import subprocess
import sys
import textwrap
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


@dc.dataclass(frozen=True)
class DeployConfig:
    python_bin: str
    app_name: str
    repo_url: str
    revision: str
    requirements_txt: str
    entrypoint: str


@dc.dataclass(frozen=True)
class HostConfig:
    username: str = 'deploy'

    global_supervisor_conf_file_path: str = '/etc/supervisor/conf.d/supervisord.conf'
    global_nginx_conf_file_path: str = '/etc/nginx/sites-enabled/deploy.conf'


class Deployment:

    def __init__(
            self,
            cfg: DeployConfig,
            host_cfg: HostConfig = HostConfig(),
    ) -> None:
        super().__init__()
        self._cfg = cfg
        self._host_cfg = host_cfg

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        _subprocess_check_call(s, shell=True)

    def ush(self, *ss: str) -> None:
        s = ' && '.join(ss)
        self.sh(f"su - {self._host_cfg.username} -c {shlex.quote(s)}")

    @cached_nullary
    def pwn(self) -> pwd.struct_passwd:
        try:
            return pwd.getpwnam(self._host_cfg.username)
        except KeyError:
            log.info('Creating user %s', self._host_cfg.username)
            self.sh(' '.join([
                'adduser',
                '--system',
                '--disabled-password',
                '--group',
                '--shell /bin/bash',
                self._host_cfg.username,
            ]))
            return pwd.getpwnam(self._host_cfg.username)

    @cached_nullary
    def home_dir(self) -> str:
        return os.path.expanduser(f'~{self._host_cfg.username}')

    @cached_nullary
    def create_dirs(self) -> None:
        pwn = self.pwn()

        for dn in [
            'app',
            'conf',
            'conf/env',
            'conf/nginx',
            'conf/supervisor',
            'venv',
        ]:
            fp = os.path.join(self.home_dir(), dn)
            if not os.path.exists(fp):
                log.info('Creating directory: %s', fp)
                os.mkdir(fp)
                os.chown(fp, pwn.pw_uid, pwn.pw_gid)

    @cached_nullary
    def create_global_nginx_conf(self) -> None:
        nginx_conf_dir = os.path.join(self.home_dir(), 'conf/nginx')
        if not os.path.isfile(self._host_cfg.global_nginx_conf_file_path):
            log.info('Writing global nginx conf at %s', self._host_cfg.global_nginx_conf_file_path)
            with open(self._host_cfg.global_nginx_conf_file_path, 'w') as f:
                f.write(f'include {nginx_conf_dir}/*.conf;\n')

    @cached_nullary
    def create_global_supervisor_conf(self) -> None:
        sup_conf_dir = os.path.join(self.home_dir(), 'conf/supervisor')
        with open(self._host_cfg.global_supervisor_conf_file_path, 'r') as f:
            glo_sup_conf = f.read()
        if sup_conf_dir not in glo_sup_conf:
            log.info('Updating global supervisor conf at %s', self._host_cfg.global_supervisor_conf_file_path)  # noqa
            glo_sup_conf += textwrap.dedent(f"""
                [include]
                files = {self.home_dir()}/conf/supervisor/*.conf
            """)
            with open(self._host_cfg.global_supervisor_conf_file_path, 'w') as f:
                f.write(glo_sup_conf)

    @cached_nullary
    def clone_repo(self) -> None:
        clone_submodules = False
        self.ush(
            'cd ~/app',
            f'git clone --depth 1 {self._cfg.repo_url} {self._cfg.app_name}',
            *([
                f'cd {self._cfg.app_name}',
                'git submodule update --init',
            ] if clone_submodules else []),
        )

    @cached_nullary
    def setup_venv(self) -> None:
        self.ush(
            'cd ~/venv',
            f'{self._cfg.python_bin} -mvenv {self._cfg.app_name}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{self._cfg.app_name}/bin/python -m ensurepip',
            f'{self._cfg.app_name}/bin/python -mpip install --upgrade setuptools pip',

            f'{self._cfg.app_name}/bin/python -mpip install -r ~deploy/app/{self._cfg.app_name}/{self._cfg.requirements_txt}',  # noqa
        )

    @cached_nullary
    def create_nginx_conf(self) -> None:
        nginx_conf = textwrap.dedent(f"""
            server {{
                listen 80;
                location / {{
                    proxy_pass http://127.0.0.1:8000/;
                }}
            }}
        """)
        nginx_conf_file = os.path.join(self.home_dir(), f'conf/nginx/{self._cfg.app_name}.conf')
        log.info('Writing nginx conf to %s', nginx_conf_file)
        with open(nginx_conf_file, 'w') as f:
            f.write(nginx_conf)

    @cached_nullary
    def create_supervisor_conf(self) -> None:
        sup_conf = textwrap.dedent(f"""
            [program:{self._cfg.app_name}]
            command={self.home_dir()}/venv/{self._cfg.app_name}/bin/python -m {self._cfg.entrypoint}
            directory={self.home_dir()}/app/{self._cfg.app_name}
            user={self._host_cfg.username}
            autostart=true
            autorestart=true
        """)
        sup_conf_file = os.path.join(self.home_dir(), f'conf/supervisor/{self._cfg.app_name}.conf')
        log.info('Writing supervisor conf to %s', sup_conf_file)
        with open(sup_conf_file, 'w') as f:
            f.write(sup_conf)

    @cached_nullary
    def deploy(self) -> None:
        self.pwn()

        self.create_dirs()

        self.create_global_nginx_conf()

        log.info('Starting nginx')
        self.sh('service nginx start')

        self.create_global_supervisor_conf()

        self.clone_repo()

        self.setup_venv()

        self.create_nginx_conf()

        self.create_supervisor_conf()

        log.info('Poking supervisor')
        self.sh('kill -HUP 1')

        log.info('Poking nginx')
        self.sh('nginx -s reload')

        log.info('Shitty deploy complete!')

##


def _main() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

    if sys.platform != 'linux':
        raise EnvironmentError('must run on linux')
    True  # type: ignore  # noqa

    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')

    Deployment(DeployConfig(
        python_bin='python3.12',
        app_name='omlish',
        repo_url='https://github.com/wrmsr/omlish',
        revision='cb60a99124c4d6973ac6e88d1a4313bcc9d8a197',
        requirements_txt='requirements.txt',
        entrypoint='omserv.server.tests.hello',
    )).deploy()


if __name__ == '__main__':
    _main()
