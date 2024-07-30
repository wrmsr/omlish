r"""
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

==

cat /etc/systemd/system/hello.service

--

[Unit]
Description=hello
After= \
    syslog.target \
    network.target \
    remote-fs.target \
    nss-lookup.target \
    network-online.target
Requires=network-online.target


[Service]
Type=simple
StandardOutput=journal
ExecStart=sleep infinity

# User=
# WorkingDirectory=

# https://serverfault.com/questions/617823/how-to-set-systemd-service-dependencies
# PIDFile=/run/nginx.pid
# ExecStartPre=/usr/sbin/nginx -t
# ExecStart=/usr/sbin/nginx
# ExecReload=/bin/kill -s HUP $MAINPID
# ExecStop=/bin/kill -s QUIT $MAINPID
# PrivateTmp=true

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

--

sudo systemctl enable hello.service
sudo systemctl start hello.service
"""  # noqa
import abc
import argparse
import dataclasses as dc
import enum
import functools
import json
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


##


class Phase(enum.Enum):
    HOST = enum.auto()
    ENV = enum.auto()
    BACKEND = enum.auto()
    FRONTEND = enum.auto()
    START_BACKEND = enum.auto()
    START_FRONTEND = enum.auto()


def run_in_phase(*ps: Phase):
    def inner(fn):
        fn.__deployment_phases__ = ps
        return fn
    return inner


class Concern(abc.ABC):
    def __init__(self, d: 'Deployment') -> None:
        super().__init__()
        self._d = d

    _phase_fns: ta.ClassVar[ta.Mapping[Phase, ta.Sequence[ta.Callable]]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        dct: ta.Dict[Phase, ta.List[ta.Callable]] = {}
        for fn, ps in [
            (v, ps)
            for a in dir(cls)
            if not (a.startswith('__') and a.endswith('__'))
            for v in [getattr(cls, a, None)]
            for ps in [getattr(v, '__deployment_phases__', None)]
            if ps
        ]:
            dct.update({p: [*dct.get(p, []), fn] for p in ps})
        cls._phase_fns = dct

    @dc.dataclass(frozen=True)
    class Output(abc.ABC):
        path: str
        is_file: bool

    def outputs(self) -> ta.Sequence[Output]:
        return ()

    def run_phase(self, p: Phase) -> None:
        for fn in self._phase_fns.get(p, ()):
            fn.__get__(self, type(self))()


##


class User(Concern):
    @run_in_phase(Phase.HOST)
    def create_user(self) -> None:
        try:
            pwd.getpwnam(self._d.host_cfg.username)
        except KeyError:
            log.info('Creating user %s', self._d.host_cfg.username)
            self._d.sh(' '.join([
                'adduser',
                '--system',
                '--disabled-password',
                '--group',
                '--shell /bin/bash',
                self._d.host_cfg.username,
            ]))
            pwd.getpwnam(self._d.host_cfg.username)


class Dirs(Concern):
    @run_in_phase(Phase.HOST)
    def create_dirs(self) -> None:
        pwn = pwd.getpwnam(self._d.host_cfg.username)

        for dn in [
            'app',
            'conf',
            'conf/env',
            'conf/nginx',
            'conf/supervisor',
            'venv',
        ]:
            fp = os.path.join(self._d.home_dir(), dn)
            if not os.path.exists(fp):
                log.info('Creating directory: %s', fp)
                os.mkdir(fp)
                os.chown(fp, pwn.pw_uid, pwn.pw_gid)


class GlobalNginx(Concern):
    @run_in_phase(Phase.HOST)
    def create_global_nginx_conf(self) -> None:
        nginx_conf_dir = os.path.join(self._d.home_dir(), 'conf/nginx')
        if not os.path.isfile(self._d.host_cfg.global_nginx_conf_file_path):
            log.info('Writing global nginx conf at %s', self._d.host_cfg.global_nginx_conf_file_path)
            with open(self._d.host_cfg.global_nginx_conf_file_path, 'w') as f:
                f.write(f'include {nginx_conf_dir}/*.conf;\n')


class GlobalSupervisor(Concern):
    @run_in_phase(Phase.HOST)
    def create_global_supervisor_conf(self) -> None:
        sup_conf_dir = os.path.join(self._d.home_dir(), 'conf/supervisor')
        with open(self._d.host_cfg.global_supervisor_conf_file_path, 'r') as f:
            glo_sup_conf = f.read()
        if sup_conf_dir not in glo_sup_conf:
            log.info('Updating global supervisor conf at %s', self._d.host_cfg.global_supervisor_conf_file_path)  # noqa
            glo_sup_conf += textwrap.dedent(f"""
                [include]
                files = {self._d.home_dir()}/conf/supervisor/*.conf
            """)
            with open(self._d.host_cfg.global_supervisor_conf_file_path, 'w') as f:
                f.write(glo_sup_conf)


class Repo(Concern):
    @run_in_phase(Phase.ENV)
    def clone_repo(self) -> None:
        clone_submodules = False
        self._d.ush(
            'cd ~/app',
            f'git clone --depth 1 {self._d.cfg.repo_url} {self._d.cfg.app_name}',
            *([
                f'cd {self._d.cfg.app_name}',
                'git submodule update --init',
            ] if clone_submodules else []),
        )


class Venv(Concern):
    @run_in_phase(Phase.ENV)
    def setup_venv(self) -> None:
        self._d.ush(
            'cd ~/venv',
            f'{self._d.cfg.python_bin} -mvenv {self._d.cfg.app_name}',

            # https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
            f'{self._d.cfg.app_name}/bin/python -m ensurepip',
            f'{self._d.cfg.app_name}/bin/python -mpip install --upgrade setuptools pip',

            f'{self._d.cfg.app_name}/bin/python -mpip install -r ~deploy/app/{self._d.cfg.app_name}/{self._d.cfg.requirements_txt}',  # noqa
        )


class Supervisor(Concern):
    @run_in_phase(Phase.BACKEND)
    def create_supervisor_conf(self) -> None:
        sup_conf = textwrap.dedent(f"""
            [program:{self._d.cfg.app_name}]
            command={self._d.home_dir()}/venv/{self._d.cfg.app_name}/bin/python -m {self._d.cfg.entrypoint}
            directory={self._d.home_dir()}/app/{self._d.cfg.app_name}
            user={self._d.host_cfg.username}
            autostart=true
            autorestart=true
        """)
        sup_conf_file = os.path.join(self._d.home_dir(), f'conf/supervisor/{self._d.cfg.app_name}.conf')
        log.info('Writing supervisor conf to %s', sup_conf_file)
        with open(sup_conf_file, 'w') as f:
            f.write(sup_conf)

    @run_in_phase(Phase.START_BACKEND)
    def poke_supervisor(self) -> None:
        log.info('Poking supervisor')
        self._d.sh('kill -HUP 1')


class Nginx(Concern):
    @run_in_phase(Phase.FRONTEND)
    def create_nginx_conf(self) -> None:
        nginx_conf = textwrap.dedent(f"""
            server {{
                listen 80;
                location / {{
                    proxy_pass http://127.0.0.1:8000/;
                }}
            }}
        """)
        nginx_conf_file = os.path.join(self._d.home_dir(), f'conf/nginx/{self._d.cfg.app_name}.conf')
        log.info('Writing nginx conf to %s', nginx_conf_file)
        with open(nginx_conf_file, 'w') as f:
            f.write(nginx_conf)

    @run_in_phase(Phase.START_FRONTEND)
    def poke_nginx(self) -> None:
        log.info('Starting nginx')
        self._d.sh('service nginx start')

        log.info('Poking nginx')
        self._d.sh('nginx -s reload')


##


class Deployment:
    concern_cls_list: ta.ClassVar[ta.List[ta.Type[Concern]]] = [
        User,
        Dirs,
        GlobalNginx,
        GlobalSupervisor,
        Repo,
        Venv,
        Supervisor,
        Nginx,
    ]

    def __init__(
            self,
            cfg: DeployConfig,
            host_cfg: HostConfig = HostConfig(),
    ) -> None:
        super().__init__()
        self._cfg = cfg
        self._host_cfg = host_cfg

        self._concerns: ta.List[Concern] = [cls(self) for cls in self.concern_cls_list]

    @property
    def cfg(self) -> DeployConfig:
        return self._cfg

    @property
    def host_cfg(self) -> HostConfig:
        return self._host_cfg

    def sh(self, *ss: str) -> None:
        s = ' && '.join(ss)
        log.info('Executing: %s', s)
        _subprocess_check_call(s, shell=True)

    def ush(self, *ss: str) -> None:
        s = ' && '.join(ss)
        self.sh(f'su - {self._host_cfg.username} -c {shlex.quote(s)}')

    @cached_nullary
    def home_dir(self) -> str:
        return os.path.expanduser(f'~{self._host_cfg.username}')

    @cached_nullary
    def deploy(self) -> None:
        for p in Phase:
            log.info('Phase %s', p.name)
            for c in self._concerns:
                c.run_phase(p)

        log.info('Shitty deploy complete!')


##


def _deploy_cmd(args) -> None:
    dct = json.loads(args.cfg)
    cfg = DeployConfig(**dct)
    dp = Deployment(cfg)
    dp.deploy()


##


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_resolve = subparsers.add_parser('deploy')
    parser_resolve.add_argument('cfg')
    parser_resolve.set_defaults(func=_deploy_cmd)

    return parser


def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

    if sys.platform != 'linux':
        raise EnvironmentError('must run on linux')
    True  # type: ignore  # noqa

    logging.root.addHandler(logging.StreamHandler())
    logging.root.setLevel('INFO')

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
