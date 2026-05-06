# ruff: noqa: UP006 UP007 UP045
"""
Runs for specified seconds, handles signals properly.

Usage: python long_runner.py [duration_seconds] [tick_interval_seconds]
"""
import signal
import sys
import time

from .helpers import err
from .helpers import log


def sigterm_handler(signum, frame):
    err(f'Received signal {signum}, exiting gracefully')
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGINT, sigterm_handler)

    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

    log(f'Started long_runner: duration={duration}s interval={interval}s pid={os.getpid()}')

    elapsed = 0.0
    tick = 0
    while elapsed < duration:
        time.sleep(interval)
        elapsed += interval
        tick += 1
        log(f'Tick {tick} elapsed={elapsed:.1f}s')

    log('Completed normally')
    sys.exit(0)


if __name__ == '__main__':
    import os
    main()
