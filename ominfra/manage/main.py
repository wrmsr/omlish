#!/usr/bin/env python3
# @omlish-amalg ../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -qs 'ssh -i foo/bar foo@bar.baz' --python=python3.8
"""
import json
import shlex
import struct
import subprocess
import typing as ta

from omlish.lite.cached import static_init
from omlish.lite.check import check_not_none
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import PolymorphicObjMarshaler
from omlish.lite.marshal import get_obj_marshaler
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import register_opj_marshaler
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from ..pyremote import PyremoteBootstrapDriver
from ..pyremote import PyremoteBootstrapOptions
from ..pyremote import pyremote_bootstrap_finalize
from ..pyremote import pyremote_build_bootstrap_cmd
from .commands.base import Command
from .commands.subprocess import SubprocessCommand
from .commands.subprocess import SubprocessCommandExecutor
from .payload import get_payload_src


##


_COMMAND_TYPES = {
    'subprocess': SubprocessCommand,
}


@static_init
def _register_command_marshaling() -> None:
    for fn in [
        lambda c: c,
        lambda c: c.Output,
    ]:
        register_opj_marshaler(
            fn(Command),
            PolymorphicObjMarshaler.of([
                PolymorphicObjMarshaler.Impl(
                    fn(cty),
                    k,
                    get_obj_marshaler(fn(cty)),
                )
                for k, cty in _COMMAND_TYPES.items()
            ]),
        )


##


def _send_obj(f: ta.IO, o: ta.Any, ty: ta.Any = None) -> None:
    j = json_dumps_compact(marshal_obj(o, ty))
    d = j.encode('utf-8')

    f.write(struct.pack('<I', len(d)))
    f.write(d)
    f.flush()


def _recv_obj(f: ta.IO, ty: ta.Any) -> ta.Any:
    d = f.read(4)
    if not d:
        return None
    if len(d) != 4:
        raise EOFError

    sz = struct.unpack('<I', d)[0]
    d = f.read(sz)
    if len(d) != sz:
        raise EOFError

    j = json.loads(d.decode('utf-8'))
    return unmarshal_obj(j, ty)


##


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    while True:
        i = _recv_obj(rt.input, Command)
        if i is None:
            break

        if isinstance(i, SubprocessCommand):
            o = SubprocessCommandExecutor().execute(i)  # noqa
        else:
            raise TypeError(i)

        _send_obj(rt.output, o, Command.Output)


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--shell')
    parser.add_argument('-q', '--shell-quote', action='store_true')
    parser.add_argument('--python', default='python3')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--_payload-file')

    args = parser.parse_args()

    #

    payload_src = get_payload_src(file=args._payload_file)  # noqa

    #

    remote_src = '\n\n'.join([
        '__name__ = "__remote__"',
        payload_src,
        '_remote_main()',
    ])

    #

    bs_src = pyremote_build_bootstrap_cmd(__package__ or 'manage')

    if args.shell is not None:
        sh_src = f'{args.python} -c {shlex.quote(bs_src)}'
        if args.shell_quote:
            sh_src = shlex.quote(sh_src)
        sh_cmd = f'{args.shell} {sh_src}'
        cmd = [sh_cmd]
        shell = True
    else:
        cmd = [args.python, '-c', bs_src]
        shell = False

    #

    proc = subprocess.Popen(
        subprocess_maybe_shell_wrap_exec(*cmd),
        shell=shell,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    stdin = check_not_none(proc.stdin)
    stdout = check_not_none(proc.stdout)

    #

    res = PyremoteBootstrapDriver(  # noqa
        remote_src,
        PyremoteBootstrapOptions(
            debug=args.debug,
        ),
    ).run(stdin, stdout)
    # print(res)

    #

    for ci in [
        SubprocessCommand(
            args=['python3', '-'],
            input=b'print(1)\n',
            capture_stdout=True,
        ),
        SubprocessCommand(
            args=['uname'],
            capture_stdout=True,
        ),
    ]:
        _send_obj(stdin, ci, Command)

        o = _recv_obj(stdout, Command.Output)

        print(o)

    try:
        stdin.close()
    except BrokenPipeError:
        pass

    proc.wait()


if __name__ == '__main__':
    _main()
