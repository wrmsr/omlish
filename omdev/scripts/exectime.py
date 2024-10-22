#!/usr/bin/env python3
# @omlish-script
import sys
import time


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'py/exectime',
    'mod_name': __name__,
}}


def _main() -> None:
    [src] = sys.argv[1:]
    co = compile(src, '<string>', 'exec')
    start = time.time_ns()
    exec(co)
    end = time.time_ns()
    print(end - start)


if __name__ == '__main__':
    _main()
