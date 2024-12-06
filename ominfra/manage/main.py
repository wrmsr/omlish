#!/usr/bin/env python3
# @omlish-amalg ../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
import dataclasses as dc
import typing as ta

from omlish.lite.inject import Injector
from omlish.lite.inject import inj
from omlish.lite.logs import configure_standard_logging
from omlish.lite.logs import log
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from ..pyremote import PyremoteBootstrapDriver
from ..pyremote import PyremoteBootstrapOptions
from ..pyremote import pyremote_bootstrap_finalize
from ..pyremote import pyremote_build_bootstrap_cmd
from .commands.base import Command
from .commands.base import CommandExecutor
from .commands.subprocess import SubprocessCommand
from .config import MainConfig
from .inject import bind_main
from .payload import get_payload_src
from .protocol import Channel
from .spawning import PySpawner


##


@dc.dataclass(frozen=True)
class MainBootstrap:
    main_config: MainConfig

    spawner_options: PySpawner.Options


def main_bootstrap(bs: MainBootstrap) -> Injector:
    if (log_level := bs.main_config.log_level) is not None:
        configure_standard_logging(log_level)

    injector = inj.create_injector(bind_main(  # noqa
        main_config=bs.main_config,
        spawner_options=bs.spawner_options,
    ))

    return injector


##


@dc.dataclass(frozen=True)
class RemoteContext:
    main_bootstrap: MainBootstrap

    pycharm_debug_port: ta.Optional[int] = None
    pycharm_debug_host: ta.Optional[str] = None
    pycharm_debug_version: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class CommandResponse:
    output: ta.Optional[Command.Output] = None
    exception: ta.Optional[str] = None


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    chan = Channel(
        rt.input,
        rt.output,
    )

    ctx = chan.recv_obj(RemoteContext)

    #

    if ctx.pycharm_debug_port is not None:
        pycharm_debug_connect(
            ctx.pycharm_debug_port,
            **(dict(host=ctx.pycharm_debug_host) if ctx.pycharm_debug_host is not None else {}),
            **(dict(install_version=ctx.pycharm_debug_version) if ctx.pycharm_debug_version is not None else {}),
        )

    #

    injector = main_bootstrap(ctx.main_bootstrap)

    #

    chan.set_marshaler(injector[ObjMarshalerManager])

    #

    ce = injector[CommandExecutor]

    #

    while True:
        i = chan.recv_obj(Command)
        if i is None:
            break

        try:
            o = ce.execute(i)
        except Exception as e:  # noqa
            log.exception('Error executing command: %r', type(i))
            r = CommandResponse(exception=repr(e))
        else:
            r = CommandResponse(output=o)

        chan.send_obj(r, CommandResponse)


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

    ##

    config = MainConfig(
        log_level='DEBUG' if args.debug else 'INFO',

        debug=bool(args.debug),
    )

    bootstrap = MainBootstrap(
        main_config=config,

        spawner_options=PySpawner.Options(
            shell=args.shell,
            shell_quote=args.shell_quote,
            python=args.python,
        ),
    )

    injector = main_bootstrap(
        bootstrap,
    )

    ##

    cmds = [
        SubprocessCommand(['python3', '-'], input=b'print(1)\n'),
        SubprocessCommand(['uname']),
        # SubprocessCommand(['barf']),
    ]

    # ce = injector[CommandExecutor]
    # msh = injector[ObjMarshalerManager]
    # for cmd in cmds:
    #     mc = msh.marshal_obj(cmd, Command)
    #     uc = msh.unmarshal_obj(mc, Command)
    #     o = ce.execute(uc)
    #     mo = msh.marshal_obj(o, Command.Output)
    #     uo = msh.unmarshal_obj(mo, Command.Output)
    #     print(uo)

    ##

    payload_src = get_payload_src(file=args._payload_file)  # noqa

    remote_src = [
        payload_src,
        '_remote_main()',
    ]

    spawn_src = pyremote_build_bootstrap_cmd(__package__ or 'manage')

    #

    with injector[PySpawner].spawn(spawn_src) as proc:
        res = PyremoteBootstrapDriver(  # noqa
            remote_src,
            PyremoteBootstrapOptions(
                debug=args.debug,
            ),
        ).run(
            proc.stdout,
            proc.stdin,
        )

        chan = Channel(
            proc.stdout,
            proc.stdin,
            msh=injector[ObjMarshalerManager],
        )

        #

        ctx = RemoteContext(
            main_bootstrap=bootstrap,

            pycharm_debug_port=args.pycharm_debug_port,
            pycharm_debug_host=args.pycharm_debug_host,
            pycharm_debug_version=args.pycharm_debug_version,
        )

        chan.send_obj(ctx)

        #

        for cmd in cmds:
            chan.send_obj(cmd, Command)

            r = chan.recv_obj(CommandResponse)

            print(r)


if __name__ == '__main__':
    _main()
