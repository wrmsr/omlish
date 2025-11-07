import argparse
import os.path
import subprocess
import typing as ta

from omlish.formats import json

from .cmdlog import CmdLog


##


DEFAULT_PROXIED_CMDS: ta.Collection[str] = [
    'ar',
    'as',
    'clang',
    'clang++',
    'g++',
    'gcc',
    'ld',
    'lld',
    'make',
]


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', nargs=argparse.REMAINDER)
    parser.add_argument('-l', '--log-file')
    parser.add_argument('-P', '--print', action='store_true')
    parser.add_argument('-p', '--proxy', action='append')
    args = parser.parse_args()

    if not args.cmd:
        parser.error('Must specify cmd')
        raise RuntimeError  # noqa

    exec_cmd, *exec_argv = args.cmd

    #

    cl = CmdLog(
        args.proxy if args.proxy is not None else DEFAULT_PROXIED_CMDS,
        log_file=os.path.abspath(args.log_file) if args.log_file is not None else None,
    )
    cl.exe()
    cl.proxy_cmds()

    rc = subprocess.call(
        [exec_cmd, *exec_argv],
        env=cl.child_env(),
    )

    if args.log_file is None or args.print:
        if os.path.exists(cl.log_file()):
            with open(cl.log_file()) as f:
                log_lines = f.readlines()
            entry_dcts = [json.loads(sl) for l in log_lines if (sl := l.strip())]
            print(json.dumps_compact(entry_dcts))

    raise SystemExit(rc)


if __name__ == '__main__':
    _main()
