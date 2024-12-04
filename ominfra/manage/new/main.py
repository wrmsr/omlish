#!/usr/bin/env python3
# @omlish-amalg ../../scripts/manage.py
# ruff: noqa: UP006 UP007
"""
manage.py -s 'docker run -i python:3.12'
manage.py -qs 'ssh -i foo/bar foo@bar.baz' --python=python3.8
"""
import inspect
import json
import shlex
import struct
import subprocess
import sys
import typing as ta

from omlish.lite.cached import cached_nullary
from omlish.lite.check import check_not_none
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import PolymorphicObjMarshaler
from omlish.lite.marshal import get_obj_marshaler
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import register_opj_marshaler
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from ...pyremote import PyremoteBootstrapDriver
from ...pyremote import PyremoteBootstrapOptions
from ...pyremote import pyremote_bootstrap_finalize
from ...pyremote import pyremote_build_bootstrap_cmd
from .commands.base import Command
from .commands.subprocess import SubprocessCommand


##


_COMMAND_TYPES = {
    'subprocess': SubprocessCommand,
}


register_opj_marshaler(
    Command.Input,
    PolymorphicObjMarshaler.of([
        PolymorphicObjMarshaler.Impl(
            cty.Input,
            k,
            get_obj_marshaler(cty.Input),
        )
        for k, cty in _COMMAND_TYPES.items()
    ]),
)

register_opj_marshaler(
    Command.Output,
    PolymorphicObjMarshaler.of([
        PolymorphicObjMarshaler.Impl(
            cty.Output,
            k,
            get_obj_marshaler(cty.Output),
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
        i = _recv_obj(rt.input, Command.Input)
        if i is None:
            break

        if isinstance(i, SubprocessCommand.Input):
            o = SubprocessCommand()._execute(i)  # noqa
        else:
            raise TypeError(i)

        _send_obj(rt.output, o, Command.Output)


##


@cached_nullary
def _get_self_src() -> str:
    return inspect.getsource(sys.modules[__name__])


def _is_src_amalg(src: str) -> bool:
    for l in src.splitlines():  # noqa
        if l.startswith('# @omlish-amalg-output '):
            return True
    return False


@cached_nullary
def _is_self_amalg() -> bool:
    return _is_src_amalg(_get_self_src())


def _get_amalg_src(*, amalg_file: ta.Optional[str]) -> str:
    if amalg_file is not None:
        with open(amalg_file) as f:
            return f.read()

    if _is_self_amalg():
        return _get_self_src()

    import importlib.resources
    return importlib.resources.files(__package__.split('.')[0] + '.scripts').joinpath('manage.py').read_text()


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--shell')
    parser.add_argument('-q', '--shell-quote', action='store_true')
    parser.add_argument('--python', default='python3')
    parser.add_argument('--_amalg-file')

    args = parser.parse_args()

    #

    amalg_src = _get_amalg_src(amalg_file=args._amalg_file)  # noqa

    #

    remote_src = '\n\n'.join([
        '__name__ = "__remote__"',
        amalg_src,
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

    proc = subprocess.Popen(
        subprocess_maybe_shell_wrap_exec(*cmd),
        shell=shell,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    stdin = check_not_none(proc.stdin)
    stdout = check_not_none(proc.stdout)

    res = PyremoteBootstrapDriver(  # noqa
        remote_src,
        PyremoteBootstrapOptions(
            # debug=True,
        ),
    ).run(stdin, stdout)
    # print(res)

    #

    for ci in [
        SubprocessCommand.Input(
            args=['python3', '-'],
            input=b'print(1)\n',
            capture_stdout=True,
        ),
        SubprocessCommand.Input(
            args=['uname'],
            capture_stdout=True,
        ),
    ]:
        _send_obj(stdin, ci, Command.Input)

        o = _recv_obj(stdout, Command.Output)

        print(o)

    try:
        stdin.close()
    except BrokenPipeError:
        pass

    proc.wait()


if __name__ == '__main__':
    _main()
