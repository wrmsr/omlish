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
import sys
import typing as ta

from omlish.argparse.cli import ArgparseCli
from omlish.argparse.cli import argparse_arg
from omlish.argparse.cli import argparse_command
from omlish.lite.logs import log  # noqa
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.marshal import ObjMarshalOptions
from omlish.lite.pycharm import PycharmRemoteDebug

from .bootstrap import MainBootstrap
from .bootstrap_ import main_bootstrap
from .commands.base import Command
from .commands.base import CommandExecutor
from .commands.local import LocalCommandExecutor
from .config import MainConfig
from .remote.config import RemoteConfig
from .remote.connection import PyremoteRemoteExecutionConnector
from .remote.spawning import RemoteSpawning


class MainCli(ArgparseCli):
    @argparse_command(
        argparse_arg('--_payload-file'),

        argparse_arg('-s', '--shell'),
        argparse_arg('-q', '--shell-quote', action='store_true'),
        argparse_arg('--python', default='python3'),

        argparse_arg('--pycharm-debug-port', type=int),
        argparse_arg('--pycharm-debug-host'),
        argparse_arg('--pycharm-debug-version'),

        argparse_arg('--remote-timebomb-delay-s', type=float),

        argparse_arg('--debug', action='store_true'),

        argparse_arg('--local', action='store_true'),

        argparse_arg('command', nargs='+'),
    )
    async def run(self) -> None:
        bs = MainBootstrap(
            main_config=MainConfig(
                log_level='DEBUG' if self.args.debug else 'INFO',

                debug=bool(self.args.debug),
            ),

            remote_config=RemoteConfig(
                payload_file=self.args._payload_file,  # noqa

                pycharm_remote_debug=PycharmRemoteDebug(
                    port=self.args.pycharm_debug_port,
                    **(dict(host=self.args.pycharm_debug_host) if self.args.pycharm_debug_host is not None else {}),
                    install_version=self.args.pycharm_debug_version,
                ) if self.args.pycharm_debug_port is not None else None,

                timebomb_delay_s=self.args.remote_timebomb_delay_s,

                # use_in_process_remote_executor=True,
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
        for c in self.args.command:
            if not c.startswith('{'):
                c = json.dumps({c: {}})
            cmd = msh.unmarshal_obj(json.loads(c), Command)
            cmds.append(cmd)

        #

        async with contextlib.AsyncExitStack() as es:
            ce: CommandExecutor

            if self.args.local:
                ce = injector[LocalCommandExecutor]

            else:
                tgt = RemoteSpawning.Target(
                    shell=self.args.shell,
                    shell_quote=self.args.shell_quote,
                    python=self.args.python,
                )

                ce = await es.enter_async_context(injector[PyremoteRemoteExecutionConnector].connect(tgt, bs))  # noqa

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
    sys.exit(asyncio.run(MainCli().async_cli_run()))


if __name__ == '__main__':
    _main()
