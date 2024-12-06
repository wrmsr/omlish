#!/usr/bin/env python3
# @omlish-amalg ../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -s 'ssh -i /foo/bar.pem foo@bar.baz' -q --python=python3.8
"""
from omlish.lite.marshal import OBJ_MARSHALER_MANAGER
from omlish.lite.marshal import ObjMarshalerManager
from omlish.lite.marshal import PolymorphicObjMarshaler

from ..pyremote import PyremoteBootstrapDriver
from ..pyremote import PyremoteBootstrapOptions
from ..pyremote import pyremote_bootstrap_finalize
from ..pyremote import pyremote_build_bootstrap_cmd
from .commands.base import Command
from .commands.subprocess import SubprocessCommand
from .commands.subprocess import SubprocessCommandExecutor
from .payload import get_payload_src
from .protocol import Channel
from .spawning import PySpawner


##


_COMMAND_TYPES = {
    'subprocess': SubprocessCommand,
}


##


def register_command_marshaling(msh: ObjMarshalerManager) -> None:
    for fn in [
        lambda c: c,
        lambda c: c.Output,
    ]:
        msh.register_opj_marshaler(
            fn(Command),
            PolymorphicObjMarshaler.of([
                PolymorphicObjMarshaler.Impl(
                    fn(cty),
                    k,
                    msh.get_obj_marshaler(fn(cty)),
                )
                for k, cty in _COMMAND_TYPES.items()
            ]),
        )


register_command_marshaling(OBJ_MARSHALER_MANAGER)


##


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa
    chan = Channel(rt.input, rt.output)

    while True:
        i = chan.recv_obj(Command)
        if i is None:
            break

        if isinstance(i, SubprocessCommand):
            o = SubprocessCommandExecutor().execute(i)  # noqa
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

        for ci in [
            SubprocessCommand(['python3', '-'], input=b'print(1)\n'),
            SubprocessCommand(['uname']),
        ]:
            chan.send_obj(ci, Command)

            o = chan.recv_obj(Command.Output)

            print(o)


if __name__ == '__main__':
    _main()
