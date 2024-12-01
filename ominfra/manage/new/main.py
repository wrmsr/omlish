#!/usr/bin/env python3
# @omlish-amalg ./_manage.py
# ruff: noqa: UP006 UP007
import inspect
import os
import shlex
import subprocess
import sys

from omlish.lite.check import check_not_none
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from ...pyremote import PyremoteBootstrapDriver
from ...pyremote import pyremote_bootstrap_finalize
from ...pyremote import pyremote_build_bootstrap_cmd
from .commands.subprocess import SubprocessCommand


##


def _run_a_command() -> None:
    i = SubprocessCommand.Input(
        args=['python3', '-'],
        input=b'print(1)\n',
        capture_stdout=True,
    )

    o = SubprocessCommand()._execute(i)  # noqa
    print(o)


def _remote_main() -> None:
    rt = pyremote_bootstrap_finalize()  # noqa

    _run_a_command()


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--ssh')
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

    if args.ssh is not None:
        sh_src = ' '.join([args.python, '-c', shlex.quote(bs_src)])
        sh_cmd = f'{args.ssh} {shlex.quote(sh_src)}'
        print(sh_cmd)
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

    print(stdout.read())
    proc.wait()


if __name__ == '__main__':
    _main()
