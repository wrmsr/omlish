# ruff: noqa: UP006 UP007 UP045
"""
Crashes immediately or after a delay with configurable exit code.

Usage: python rapid_crasher.py [exit_code] [delay_seconds]
"""
import os
import sys
import time

from .helpers import log


def main():
    exit_code = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0

    log(f'Started rapid_crasher: code={exit_code} delay={delay}s pid={os.getpid()}')

    if delay > 0:
        time.sleep(delay)

    log(f'Crashing with code {exit_code}')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
