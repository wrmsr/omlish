#!/usr/bin/env python3
# @omlish-script


##


def _run_one(src, pre=None):
    import time

    if pre:
        exec(pre)

    co = compile(src, '<string>', 'exec')
    start = time.time_ns()
    exec(co)
    end = time.time_ns()

    return end - start


##


def _run(n, src, pre=None):
    if n is None:
        return _run_one(src, pre=pre)

    #

    import inspect

    cmd = '\n'.join([
        inspect.getsource(_run_one),
        f'print(_run_one({src!r}, pre={pre!r}))',
    ])

    #

    import subprocess
    import sys

    ts = []
    for _ in range(n):
        out = subprocess.check_output([sys.executable, '-c', cmd]).decode()
        t = int(out.strip())
        ts.append(t)

    #

    import statistics

    o = {
        # 'times': ts,
        'mean': statistics.mean(ts),
        'median': statistics.median(ts),
        'quantiles': statistics.quantiles(ts),
    }

    return o


##


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'py/exectime',
    'mod_name': __name__,
}}


def _main():
    import sys

    args = sys.argv[1:]

    n = None
    if args:
        try:
            n = int(args[0])
        except ValueError:
            pass
        else:
            args.pop(0)

    if len(args) > 1:
        pre = args.pop(0)
    else:
        pre = None

    if len(args) != 1:
        raise Exception('Invalid arguments')
    [src] = args

    #

    o = _run(n, src, pre=pre)

    import json

    print(json.dumps(o, indent=2))


if __name__ == '__main__':
    _main()
