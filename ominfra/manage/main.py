#!/usr/bin/env python3
# @omlish-amalg ../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
import contextlib
import typing as ta

from omlish.lite.logs import log  # noqa
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.marshal import ObjMarshalOptions
from omlish.lite.pycharm import PycharmRemoteDebug

from .bootstrap import MainBootstrap
from .bootstrap_ import main_bootstrap
from .commands.base import Command
from .commands.base import CommandExecutor
from .commands.execution import LocalCommandExecutor
from .commands.subprocess import SubprocessCommand
from .config import MainConfig
from .deploy.command import DeployCommand
from .remote.config import RemoteConfig
from .remote.execution import RemoteExecution
from .remote.spawning import RemoteSpawning


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--_payload-file')

    parser.add_argument('-s', '--shell')
    parser.add_argument('-q', '--shell-quote', action='store_true')
    parser.add_argument('--python', default='python3')

    parser.add_argument('--pycharm-debug-port', type=int)
    parser.add_argument('--pycharm-debug-host')
    parser.add_argument('--pycharm-debug-version')

    parser.add_argument('--debug', action='store_true')

    parser.add_argument('--local', action='store_true')

    parser.add_argument('command', nargs='+')

    args = parser.parse_args()

    #

    bs = MainBootstrap(
        main_config=MainConfig(
            log_level='DEBUG' if args.debug else 'INFO',

            debug=bool(args.debug),
        ),

        remote_config=RemoteConfig(
            payload_file=args._payload_file,  # noqa

            pycharm_remote_debug=PycharmRemoteDebug(
                port=args.pycharm_debug_port,
                host=args.pycharm_debug_host,
                install_version=args.pycharm_debug_version,
            ) if args.pycharm_debug_port is not None else None,
        ),
    )

    injector = main_bootstrap(
        bs,
    )

    #

    cmds: ta.List[Command] = []
    for c in args.command:
        if c == 'deploy':
            cmds.append(DeployCommand())
        else:
            cmds.append(SubprocessCommand([c]))

    #

    with contextlib.ExitStack() as es:
        ce: CommandExecutor

        if args.local:
            ce = injector[LocalCommandExecutor]

        else:
            tgt = RemoteSpawning.Target(
                shell=args.shell,
                shell_quote=args.shell_quote,
                python=args.python,
            )

            ce = es.enter_context(injector[RemoteExecution].connect(tgt, bs))  # noqa

        for cmd in cmds:
            r = ce.try_execute(cmd)

            print(injector[ObjMarshalerManager].marshal_obj(r, opts=ObjMarshalOptions(raw_bytes=True)))


if __name__ == '__main__':
    _main()
