#!/usr/bin/env python3
# @omlish-amalg ../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
import dataclasses as dc
import typing as ta

from omlish.lite.inject import inj
from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from ..pyremote import PyremoteBootstrapDriver
from ..pyremote import PyremoteBootstrapOptions
from ..pyremote import pyremote_bootstrap_finalize
from ..pyremote import pyremote_build_bootstrap_cmd
from .commands.base import Command
from .commands.base import CommandExecutor
from .commands.base import build_command_name_map
from .commands.subprocess import SubprocessCommand
from .commands.subprocess import SubprocessCommandExecutor
from .payload import get_payload_src
from .protocol import Channel
from .spawning import PySpawner
from .marshal import install_command_marshaling


##


@dc.dataclass(frozen=True)
class RemoteContext:
    pycharm_debug_port: ta.Optional[int] = None
    pycharm_debug_host: ta.Optional[str] = None
    pycharm_debug_version: ta.Optional[str] = None


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa
    chan = Channel(rt.input, rt.output)
    ctx = chan.recv_obj(RemoteContext)

    #

    if ctx.pycharm_debug_port is not None:
        pycharm_debug_connect(
            ctx.pycharm_debug_port,
            **(dict(host=ctx.pycharm_debug_host) if ctx.pycharm_debug_host is not None else {}),
            **(dict(install_version=ctx.pycharm_debug_version) if ctx.pycharm_debug_version is not None else {}),
        )

    #

    while True:
        i = chan.recv_obj(Command)
        if i is None:
            break

        if isinstance(i, SubprocessCommand):
            o = i.execute(SubprocessCommandExecutor())
        else:
            raise TypeError(i)

        chan.send_obj(o, Command.Output)


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

    args = parser.parse_args()

    #

    payload_src = get_payload_src(file=args._payload_file)  # noqa

    remote_src = '\n\n'.join([
        '__name__ = "__remote__"',
        payload_src,
        '_remote_main()',
    ])

    #

    spawner = PySpawner(
        pyremote_build_bootstrap_cmd(__package__ or 'manage'),
        shell=args.shell,
        shell_quote=args.shell_quote,
        python=args.python,
    )

    with spawner.spawn() as proc:
        res = PyremoteBootstrapDriver(  # noqa
            remote_src,
            PyremoteBootstrapOptions(
                debug=args.debug,
            ),
        ).run(proc.stdout, proc.stdin)

        chan = Channel(proc.stdout, proc.stdin)

        #

        ctx = RemoteContext(
            pycharm_debug_port=args.pycharm_debug_port,
            pycharm_debug_host=args.pycharm_debug_host,
            pycharm_debug_version=args.pycharm_debug_version,
        )

        chan.send_obj(ctx)

        #

        for ci in [
            SubprocessCommand(['python3', '-'], input=b'print(1)\n'),
            SubprocessCommand(['uname']),
        ]:
            chan.send_obj(ci, Command)

            o = chan.recv_obj(Command.Output)

            print(o)


if __name__ == '__main__':
    _main()
