#!/usr/bin/env python3
# @omlish-amalg ../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
import asyncio
import contextlib
import json
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
from .config import MainConfig
from .remote.config import RemoteConfig
from .remote.connection import RemoteExecutionConnector
from .remote.spawning import RemoteSpawning


##


async def _async_main(args: ta.Any) -> None:
    bs = MainBootstrap(
        main_config=MainConfig(
            log_level='DEBUG' if args.debug else 'INFO',

            debug=bool(args.debug),
        ),

        remote_config=RemoteConfig(
            payload_file=args._payload_file,  # noqa

            pycharm_remote_debug=PycharmRemoteDebug(
                port=args.pycharm_debug_port,
                **(dict(host=args.pycharm_debug_host) if args.pycharm_debug_host is not None else {}),
                install_version=args.pycharm_debug_version,
            ) if args.pycharm_debug_port is not None else None,

            timebomb_delay_s=args.remote_timebomb_delay_s,
        ),
    )

    #

    injector = main_bootstrap(
        bs,
    )

    #

    msh = injector[ObjMarshalerManager]

    cmds: ta.List[Command] = []
    cmd: Command
    for c in args.command:
        if not c.startswith('{'):
            c = json.dumps({c: {}})
        cmd = msh.unmarshal_obj(json.loads(c), Command)
        cmds.append(cmd)

    #

    async with contextlib.AsyncExitStack() as es:
        ce: CommandExecutor

        if args.local:
            ce = injector[LocalCommandExecutor]

        else:
            tgt = RemoteSpawning.Target(
                shell=args.shell,
                shell_quote=args.shell_quote,
                python=args.python,
            )

            ce = await es.enter_async_context(injector[RemoteExecutionConnector].connect(tgt, bs))  # noqa

        async def run_command(cmd: Command) -> None:
            res = await ce.try_execute(
                cmd,
                log=log,
                omit_exc_object=True,
            )

            print(msh.marshal_obj(res, opts=ObjMarshalOptions(raw_bytes=True)))

        await asyncio.gather(*[
            run_command(cmd)
            for cmd in cmds
        ])


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

    parser.add_argument('--remote-timebomb-delay-s', type=float)

    parser.add_argument('--debug', action='store_true')

    parser.add_argument('--local', action='store_true')

    parser.add_argument('command', nargs='+')

    args = parser.parse_args()

    #

    asyncio.run(_async_main(args))


if __name__ == '__main__':
    _main()
