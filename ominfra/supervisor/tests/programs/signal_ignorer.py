# ruff: noqa: UP006 UP007 UP045
"""
Ignores SIGTERM to test SIGKILL escalation.

Usage: python signal_ignorer.py [tick_interval_seconds]
"""
import os
import signal
import sys
import time

from .helpers import log


def main():
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    interval = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0

    log(f'Started signal_ignorer: ignoring SIGTERM pid={os.getpid()}')

    tick = 0
    while True:
        time.sleep(interval)
        tick += 1
        log(f'Still running... tick={tick}')


if __name__ == '__main__':
    main()
