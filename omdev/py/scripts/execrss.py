#!/usr/bin/env python3
# @omlish-script
import resource
import sys


def _get_rss() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


# @omlish-manifest
_CLI_MODULE = {'$omdev.cli.types.CliModule': {
    'cmd_name': 'py/execrss',
    'mod_name': __name__,
}}


def _main() -> None:
    if len(sys.argv) == 2:
        pre = None
        [src] = sys.argv[1:]
    elif len(sys.argv) == 3:
        [pre, src] = sys.argv[1:]
    else:
        raise Exception('Invalid arguments')

    if pre:
        exec(pre)

    start = _get_rss()
    exec(src)
    end = _get_rss()
    print(end - start)


if __name__ == '__main__':
    _main()
