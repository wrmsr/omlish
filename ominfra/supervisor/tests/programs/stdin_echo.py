# ruff: noqa: UP006 UP007 UP045
"""
Echoes stdin to stdout line by line.

Usage: python stdin_echo.py
"""
import os
import sys

from .helpers import log


def main():
    log(f'Started stdin_echo pid={os.getpid()}')

    try:
        for line in sys.stdin:
            sys.stdout.write(f'ECHO: {line}')
            sys.stdout.flush()
    except KeyboardInterrupt:
        log('Interrupted')

    log('stdin closed, exiting')
    sys.exit(0)


if __name__ == '__main__':
    main()
