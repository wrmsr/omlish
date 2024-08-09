#!/usr/bin/env python3
# @omdev-amalg _amalg.py
r"""
TODO:
 - flock
 - interp.py

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
import argparse
import json
import sys
import typing as ta

from omdev.amalg.std.logging import setup_standard_logging
from omdev.amalg.std.runtime import check_runtime_version

from ..configs import DeployConfig
from .base import Deployment
from .concerns.dirs import Dirs
from .concerns.nginx import GlobalNginx
from .concerns.nginx import Nginx
from .concerns.repo import Repo
from .concerns.supervisor import GlobalSupervisor
from .concerns.supervisor import Supervisor
from .concerns.user import User
from .concerns.venv import Venv


##


def _deploy_cmd(args) -> None:
    dct = json.loads(args.cfg)
    cfg = DeployConfig(**dct)
    dp = Deployment(
        cfg,
        [
            User,
            Dirs,
            GlobalNginx,
            GlobalSupervisor,
            Repo,
            Venv,
            Supervisor,
            Nginx,
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

    setup_standard_logging()

    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, 'func', None):
        parser.print_help()
    else:
        args.func(args)


if __name__ == '__main__':
    _main()
