#!/usr/bin/env python3
import resource
import sys


def _get_rss() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def _main() -> None:
    [src] = sys.argv[1:]
    start = _get_rss()
    exec(src)
    end = _get_rss()
    print(end - start)


if __name__ == '__main__':
    _main()
