#!/usr/bin/env python3
# @omlish-amalg ./_manage.py
# ruff: noqa: UP006 UP007
import inspect
import json
import os
import shlex
import struct
import subprocess
import sys
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from ...pyremote import PyremoteBootstrapDriver
from ...pyremote import pyremote_bootstrap_finalize
from ...pyremote import pyremote_build_bootstrap_cmd
from .commands.subprocess import SubprocessCommand


##


def _send_obj(f: ta.IO, o: ta.Any) -> None:
    j = json_dumps_compact(marshal_obj(o))
    d = j.encode('utf-8')

    f.write(struct.pack('<I', len(d)))
    f.write(d)
    f.flush()


def _recv_obj(f: ta.IO, ty: type) -> ta.Any:
    d = f.read(4)
    if not d:
        return None
    if len(d) != 4:
        raise Exception

    sz = struct.unpack('<I', d)[0]
    d = f.read(sz)
    if not d:
        raise Exception

    j = json.loads(d.decode('utf-8'))
    return unmarshal_obj(j, ty)


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    while True:
        i = _recv_obj(rt.input, SubprocessCommand.Input)
        if i is None:
            break

        o = SubprocessCommand()._execute(i)  # noqa

        _send_obj(rt.output, o)


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--shell')
    parser.add_argument('-q', '--shell-quote', action='store_true')
    parser.add_argument('--python', default='python3')
    parser.add_argument('--_amalg-file')

    args = parser.parse_args()

    #

    self_src = inspect.getsource(sys.modules[__name__])
    self_src_lines = self_src.splitlines()
    for l in self_src_lines:
        if l.startswith('# @omlish-amalg-output '):
            is_self_amalg = True
            break
    else:
        is_self_amalg = False

    if is_self_amalg:
        amalg_src = self_src
    else:
        amalg_file = args._amalg_file  # noqa
        if amalg_file is None:
            amalg_file = os.path.join(os.path.dirname(__file__), '_manage.py')
        with open(amalg_file) as f:
            amalg_src = f.read()

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

    res = PyremoteBootstrapDriver(remote_src).run(stdin, stdout)
    print(res)

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
        _send_obj(stdin, ci)

        o = _recv_obj(stdout, SubprocessCommand.Output)

        print(o)

    try:
        stdin.close()
    except BrokenPipeError:
        pass

    proc.wait()


if __name__ == '__main__':
    _main()
