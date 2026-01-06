"""
TODO:
 - sqlite
 - unify-ish with omlish.sql
"""
import abc
import configparser
import dataclasses as dc
import os.path
import shutil
import sys
import typing as ta
import urllib.parse
import warnings

import yaml

from omlish import check
from omlish import lang
from omlish.argparse import all as ap
from omlish.logs import all as logs

from ..cli import CliModule


##


@dc.dataclass(frozen=True)
class ServerSpec:
    host: str
    port: int | None = None
    username: str | None = None
    password: str | None = None
    db: str | None = None

    @classmethod
    def from_url(cls, url: str) -> 'ServerSpec':
        parsed = urllib.parse.urlparse(url)
        if not parsed.hostname:
            raise NameError(parsed.hostname)
        if parsed.path:
            if not parsed.path.startswith('/'):
                raise NameError(parsed.path)
            db = parsed.path[1:]
        else:
            db = None
        return ServerSpec(
            host=parsed.hostname,
            port=parsed.port or None,
            username=parsed.username or None,
            password=parsed.password or None,
            db=db,
        )


def spec_from_mysql_docker_compose(svc: ta.Mapping[str, ta.Any]) -> ServerSpec:
    env = svc['environment']
    return ServerSpec(
        host='localhost',
        port=int(svc['ports'][0].split(':')[0]),
        username=env.get('MYSQL_USER') or None,
        password=env.get('MYSQL_PASSWORD') or None,
    )


def spec_from_postgres_docker_compose(svc: ta.Mapping[str, ta.Any]) -> ServerSpec:
    env = svc['environment']
    return ServerSpec(
        host='localhost',
        port=int(svc['ports'][0].split(':')[0]),
        username=env.get('POSTGRES_USER') or None,
        password=env.get('POSTGRES_PASSWORD') or None,
    )


def spec_from_cfg(cfg: ta.Mapping[str, ta.Any], prefix: str) -> ServerSpec:
    return ServerSpec(
        host=cfg[prefix + '_host'],
        port=cfg.get(prefix + '_port'),
        username=cfg.get(prefix + '_user'),
        password=cfg.get(prefix + '_pass'),
    )


##


@dc.dataclass(frozen=True)
class ReplArgs:
    spec: ServerSpec
    extra_args: ta.Sequence[str] | None = None  # noqa

    _: dc.KW_ONLY

    exe: ta.Sequence[str] | None = None

    no_dbcli: bool = False
    no_import: bool = False
    no_uv: bool = False
    dbcli_version: str | None = None


class ReplRunner(lang.Abstract):
    def __init__(self, args: ReplArgs) -> None:
        super().__init__()

        self._args = args

    exe_name: ta.ClassVar[str]
    dbcli_name: ta.ClassVar[str | None] = None

    #

    class Exe(ta.NamedTuple):
        args: ta.Sequence[str]
        is_dbcli: bool

    @lang.cached_function
    def exe(self) -> Exe:
        if self._args.exe is not None:
            if isinstance(self._args.exe, str):
                return ReplRunner.Exe([self._args.exe], False)
            else:
                return ReplRunner.Exe(list(self._args.exe), False)

        def default():
            return ReplRunner.Exe([check.not_none(shutil.which(self.exe_name))], False)

        if self._args.no_dbcli or self.dbcli_name is None:
            return default()

        if not self._args.no_import:
            main_mod = self.dbcli_name + '.main'

            try:
                __import__(main_mod)
            except ImportError:
                pass
            else:
                return ReplRunner.Exe([sys.executable, '-m', main_mod], True)

        if not self._args.no_uv and (uv_exe := shutil.which('uv')) is not None:
            uv_arg = self.dbcli_name
            if self._args.dbcli_version is not None:
                uv_arg += f'@{self._args.dbcli_version}'

            return ReplRunner.Exe([uv_exe, 'tool', 'run', uv_arg], True)

        return default()

    #

    @abc.abstractmethod
    def build_args(self) -> ta.Sequence[str]:
        raise NotImplementedError

    def pre_exec(self) -> None:
        pass

    #

    def run(self) -> ta.NoReturn:
        lst: list[str] = [
            *self.exe().args,
            *self.build_args(),
        ]

        self.pre_exec()

        os.execvp(lst[0], lst)


class MysqlReplRunner(ReplRunner):
    dbcli_name = 'mycli'
    exe_name = 'mysql'

    def build_args(self) -> ta.Sequence[str]:
        lst: list[str] = []

        if self._args.spec.username:
            lst.extend(['--user', self._args.spec.username])

        lst.extend(['--host', self._args.spec.host])
        if not self.exe().is_dbcli:
            lst.append('--protocol=TCP')
        if self._args.spec.port:
            lst.extend(['--port', str(self._args.spec.port)])

        if self._args.spec.db:
            lst.append(self._args.spec.db)

        lst.extend(self._args.extra_args or [])

        return lst

    def pre_exec(self) -> None:
        super().pre_exec()

        if self._args.spec.password:
            os.environ['MYSQL_PWD'] = self._args.spec.password


class PostgresReplRunner(ReplRunner):
    dbcli_name = 'pgcli'
    exe_name = 'psql'

    def build_args(self) -> ta.Sequence[str]:
        lst: list[str] = []

        if self._args.spec.username:
            lst.extend(['--username', self._args.spec.username])

        if self._args.spec.host:
            lst.extend(['--host', self._args.spec.host])
        if self._args.spec.port:
            lst.extend(['--port', str(self._args.spec.port)])

        if self._args.spec.db:
            lst.append(self._args.spec.db)

        lst.extend(self._args.extra_args or [])

        return lst

    def _maybe_warn_keyring(self) -> None:
        if 'XDG_CONFIG_HOME' in os.environ:
            cfg_dir = f'{os.path.expanduser(os.environ["XDG_CONFIG_HOME"])}/pgcli/'
        else:
            cfg_dir = os.path.expanduser('~/.config/pgcli/')
        cfg_path = os.path.join(cfg_dir, 'config')

        if os.path.exists(cfg_path):
            cfg = configparser.ConfigParser()
            cfg.read(cfg_path)

            if cfg.has_section('main') and not cfg.getboolean('main', 'keyring', fallback=True):
                return

        warnings.warn(
            'pgcli keyring is not disabled, it will try to store credentials. '
            'set `[main] keyring = False` in ~/.config/pgcli/config',
        )

    def pre_exec(self) -> None:
        super().pre_exec()

        self._maybe_warn_keyring()

        if self._args.spec.password:
            os.environ['PGPASSWORD'] = self._args.spec.password


##


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('dialect'),
        ap.arg('target'),
        ap.arg('args', nargs='*'),
        ap.arg('--no-dbcli', action='store_true'),
        ap.arg('--no-import', action='store_true'),
        ap.arg('--no-uv', action='store_true'),
    )
    def repl(self) -> None:
        l, _, r = (target := self.args.target).partition(':')
        _, lf = os.path.dirname(l), os.path.basename(l)
        if not lf.endswith('.yml'):
            raise Exception(f'unhandled target: {target=}')

        with open(l) as f:
            cfg = yaml.safe_load(f.read())

        dialect = self.args.dialect

        if lf == 'compose.yml':
            svc = cfg['services'][r]
            if dialect == 'mysql':
                spec = spec_from_mysql_docker_compose(svc)
            elif dialect == 'postgres':
                spec = spec_from_postgres_docker_compose(svc)
            else:
                raise Exception(f'unhandled dialect: {dialect=}')
        else:
            spec = spec_from_cfg(cfg, r)

        repl_args = ReplArgs(
            spec,
            self.args.args,
            no_dbcli=self.args.no_dbcli,
            no_import=self.args.no_import,
            no_uv=self.args.no_uv,
        )

        repl_run: ReplRunner
        if dialect == 'mysql':
            repl_run = MysqlReplRunner(repl_args)
        elif dialect == 'postgres':
            repl_run = PostgresReplRunner(repl_args)
        else:
            raise Exception(f'unhandled dialect: {dialect=}')

        repl_run.run()


# @omlish-manifest
_CLI_MODULE = CliModule('sqlrepl', __name__)


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
