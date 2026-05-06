# ruff: noqa: UP006 UP007 UP045
"""
Exits immediately with configurable exit code and optional delay.

Usage: python immediate_exit.py [exit_code] [delay_seconds]
"""
import os
import sys
import time

from .helpers import log


##


def main() -> None:
    exit_code = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0

    log(f'Started immediate_exit: code={exit_code} delay={delay}s pid={os.getpid()}')

    if delay > 0:
        log(f'Waiting {delay}s before exit')
        time.sleep(delay)

    log(f'Exiting with code {exit_code}')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
