#!/usr/bin/env python3
# @omlish-amalg ../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
import dataclasses as dc
import typing as ta

from omlish.lite.logs import log
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.pycharm import pycharm_debug_connect

from ..pyremote import PyremoteBootstrapDriver
from ..pyremote import PyremoteBootstrapOptions
from ..pyremote import pyremote_bootstrap_finalize
from ..pyremote import pyremote_build_bootstrap_cmd
from .bootstrap import MainBootstrap
from .bootstrap import main_bootstrap
from .commands.base import Command
from .commands.base import CommandExecutor
from .commands.base import CommandOutputOrExceptionData
from .commands.subprocess import SubprocessCommand
from .config import MainConfig
from .payload import get_payload_src
from .protocol import Channel
from .remote import RemoteSpawning


##


@dc.dataclass(frozen=True)
class RemoteContext:
    main_bootstrap: MainBootstrap

    @dc.dataclass(frozen=True)
    class PycharmDebug:
        port: int
        host: ta.Optional[str] = None
        install_version: ta.Optional[str] = None

    pycharm_debug: ta.Optional[PycharmDebug] = None


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    chan = Channel(
        rt.input,
        rt.output,
    )

    ctx = chan.recv_obj(RemoteContext)

    #

    if (pd := ctx.pycharm_debug) is not None:
        pycharm_debug_connect(
            pd.port,
            **(dict(host=pd.host) if pd.host is not None else {}),
            **(dict(install_version=pd.install_version) if pd.install_version is not None else {}),
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

        r = ce.try_execute(
            i,
            log=log,
            omit_exc_object=True,
        )

        chan.send_obj(r)


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

        remote_spawning_options=RemoteSpawning.Options(
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

    ce = injector[CommandExecutor]
    msh = injector[ObjMarshalerManager]
    for cmd in cmds:
        mc = msh.roundtrip_obj(cmd, Command)
        r = ce.try_execute(mc)
        mr = msh.roundtrip_obj(r, CommandOutputOrExceptionData)
        print(mr)

    ##

    payload_src = get_payload_src(file=args._payload_file)  # noqa

    remote_src = [
        payload_src,
        '_remote_main()',
    ]

    spawn_src = pyremote_build_bootstrap_cmd(__package__ or 'manage')

    #

    with injector[RemoteSpawning].spawn(spawn_src) as proc:
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

            pycharm_debug=RemoteContext.PycharmDebug(
                port=args.pycharm_debug_port,
                host=args.pycharm_debug_host,
                install_version=args.pycharm_debug_version,
            ) if args.pycharm_debug_port is not None else None,
        )

        chan.send_obj(ctx)

        #

        for cmd in cmds:
            chan.send_obj(cmd, Command)

            r = chan.recv_obj(CommandOutputOrExceptionData)

            print(r)


if __name__ == '__main__':
    _main()
