#!/usr/bin/env python3
# @omlish-amalg ../_executor.py
r"""
TODO:
 - flock
 - interp.py
 - systemd

deployment matrix
 - os: ubuntu / amzn / generic
 - arch: amd64 / arm64
 - host: bare / docker
 - init: supervisor-provided / supervisor-must-configure / systemd (/ self?)
 - interp: system / pyenv / interp.py
 - venv: none / yes
 - nginx: no / provided / must-configure

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
"""  # noqa
# ruff: noqa: UP007
import argparse
import json
import sys
import typing as ta

from omlish.lite.logs import configure_standard_logging
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.runtime import check_runtime_version

from ..configs import DeployConfig
from .base import Deployment
from .concerns.dirs import DirsConcern
from .concerns.nginx import GlobalNginxConcern
from .concerns.nginx import NginxConcern
from .concerns.repo import RepoConcern
from .concerns.supervisor import GlobalSupervisorConcern
from .concerns.supervisor import SupervisorConcern
from .concerns.user import UserConcern
from .concerns.venv import VenvConcern


##


def _deploy_cmd(args) -> None:
    dct = json.loads(args.cfg)
    cfg: DeployConfig = unmarshal_obj(dct, DeployConfig)
    dp = Deployment(
        cfg,
        [
            UserConcern,
            DirsConcern,
            GlobalNginxConcern,
            GlobalSupervisorConcern,
            RepoConcern,
            VenvConcern,
            SupervisorConcern,
            NginxConcern,
        ],
    )
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
    check_runtime_version()

    if getattr(sys, 'platform') != 'linux':  # noqa
        raise OSError('must run on linux')

    configure_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
