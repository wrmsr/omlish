# ruff: noqa: UP006 UP007 UP045
"""
Takes time to 'start up', then runs normally.

Usage: python slow_starter.py [startup_delay_seconds] [run_duration_seconds]
"""
import os
import signal
import sys
import time

from .helpers import log


##


def sigterm_handler(signum, frame):
    log(f'Received signal {signum}, exiting')
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, sigterm_handler)

    startup_delay = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
    run_duration = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0

    log(f'Started slow_starter: startup={startup_delay}s run={run_duration}s pid={os.getpid()}')

    log(f'Starting up (will take {startup_delay}s)...')
    time.sleep(startup_delay)

    log('Startup complete, now running normally')

    elapsed = 0.0
    while elapsed < run_duration:
        time.sleep(1.0)
        elapsed += 1.0
        if int(elapsed) % 5 == 0:
            log(f'Running: {elapsed:.0f}s')

    log('Completed normally')
    sys.exit(0)


if __name__ == '__main__':
    main()
