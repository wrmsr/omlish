#!/usr/bin/env python3
"""
Responsibilities:
 - docker-compose or secrets
 - dbcli where available, fallback on cli
"""
import argparse
import dataclasses as dc
import os
import typing as ta
import sys
import urllib.parse

import yaml


@dc.dataclass(frozen=True)
class ServerSpec:
    host: str
    port: ta.Optional[int] = None
    username: ta.Optional[str] = None
    password: ta.Optional[str] = None
    db: ta.Optional[str] = None

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


def spec_from_secrets(cfg: ta.Mapping[str, ta.Any], prefix: str) -> ServerSpec:
    return ServerSpec(
        host=cfg[prefix + '_host'],
        port=cfg.get(prefix + '_port'),
        username=cfg.get(prefix + '_user'),
        password=cfg.get(prefix + '_pass'),
    )


def _dbcli_or_fallback_exe(dbcli_mod: str, default_exe: str) -> ta.Sequence[str]:
    main_mod = dbcli_mod + '.main'
    try:
        __import__(main_mod)
    except ImportError:
        return default_exe
    return [sys.executable, '-m', main_mod]

def exec_mysql_cli(
        exe: ta.Sequence[str],
        spec: ServerSpec,
        *extra_args: str,
) -> ta.NoReturn:
    # args = [exe] if exe is not None else list(_dbcli_or_fallback_exe('mycli', 'mysql'))
    args = list(exe)
    if spec.username:
        args.extend(['--user', spec.username])
    if spec.password:
        os.environ['MYSQL_PWD'] = spec.password
    args.extend(['--host', spec.host])
    if spec.port:
        args.extend(['--port', str(spec.port)])
    if spec.db:
        args.append(spec.db)
    args.extend(extra_args)
    os.execvp(args[0], args)


def exec_postgres_cli(
        exe: ta.Sequence[str],
        spec: ServerSpec,
        *extra_args: str,
) -> ta.NoReturn:
    # args = [exe] if exe is not None else list(_dbcli_or_fallback_exe('pgcli', 'psql'))
    args = list(exe)
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


def _main():
    with open('docker/docker-compose.yml') as f:
        dc_cfg = yaml.safe_load(f.read())

    print(dc_cfg)


# def _build_parser() -> argparse.ArgumentParser:
#     parser = argparse.ArgumentParser()
#
#     subparsers = parser.add_subparsers()
#
#     parser_resolve = subparsers.add_parser('venv')
#     parser_resolve.add_argument('name')
#     parser_resolve.add_argument('interp')
#     parser_resolve.add_argument('--debug', action='store_true')
#     parser_resolve.set_defaults(func=_venv_cmd)
#
#     return parser
#
#
# def _main(argv: ta.Optional[ta.Sequence[str]] = None) -> None:
#     parser = _build_parser()
#     args = parser.parse_args(argv)
#     if not getattr(args, 'func', None):
#         parser.print_help()
#     else:
#         args.func(args)


if __name__ == '__main__':
    _main()
