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


@lang.cached_function
def _maybe_warn_pgcli_keyring() -> None:
    import pgcli.config

    c = pgcli.config.get_config()
    if c['main'].as_bool('keyring'):
        warnings.warn(
            'pgcli keyring is not disabled, it will try to store credentials. '
            'set `keyring = False` in ~/.config/pgcli/config',
        )


def _dbcli_or_fallback_exe(dbcli_mod: str | None, default_exe: str) -> tuple[ta.Sequence[str], bool]:
    if dbcli_mod is not None:
        main_mod = dbcli_mod + '.main'
        try:
            __import__(main_mod)
        except ImportError:
            pass
        else:
            if dbcli_mod == 'pgcli':
                _maybe_warn_pgcli_keyring()
            return [sys.executable, '-m', main_mod], True
    return [check.not_none(shutil.which(default_exe))], False


def exec_mysql_cli(
        spec: ServerSpec,
        *extra_args: str,
        exe: ta.Iterable[str] | None = None,
        no_dbcli: bool = False,
) -> ta.NoReturn:
    if exe is not None:
        args, is_dbcli = list(exe), False
    else:
        argsx, is_dbcli = _dbcli_or_fallback_exe(
            'mycli' if not no_dbcli else None,
            'mysql',
        )
        args = list(argsx)
    if spec.username:
        args.extend(['--user', spec.username])
    if spec.password:
        os.environ['MYSQL_PWD'] = spec.password
    args.extend(['--host', spec.host])
    if not is_dbcli:
        args.append('--protocol=TCP')
    if spec.port:
        args.extend(['--port', str(spec.port)])
    if spec.db:
        args.append(spec.db)
    args.extend(extra_args)
    os.execvp(args[0], args)


def exec_postgres_cli(
        spec: ServerSpec,
        *extra_args: str,
        exe: ta.Iterable[str] | None = None,
        no_dbcli: bool = False,
) -> ta.NoReturn:
    if exe is not None:
        args, is_dbcli = list(exe), False
    else:
        argsx, is_dbcli = _dbcli_or_fallback_exe(
            'pgcli' if not no_dbcli else None,
            'psql',
        )
        args = list(argsx)
    if spec.username:
        args.extend(['--username', spec.username])
    if spec.password:
        os.environ['PGPASSWORD'] = spec.password
    if spec.host:
        args.extend(['--host', spec.host])
    if spec.port:
        args.extend(['--port', str(spec.port)])
    if spec.db:
        args.append(spec.db)
    args.extend(extra_args)
    os.execvp(args[0], args)


class Cli(ap.Cli):
    @ap.cmd(
        ap.arg('--no-dbcli', action='store_true'),
        ap.arg('dialect'),
        ap.arg('target'),
        ap.arg('args', nargs='*'),
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

        if dialect == 'mysql':
            exec_mysql_cli(spec, *self.args.args, no_dbcli=self.args.no_dbcli)
        elif dialect == 'postgres':
            exec_postgres_cli(spec, *self.args.args, no_dbcli=self.args.no_dbcli)
        else:
            raise Exception(f'unhandled dialect: {dialect=}')


# @omlish-manifest
_CLI_MODULE = CliModule('sqlrepl', __name__)


if __name__ == '__main__':
    logs.configure_standard_logging('INFO')
    Cli()()
