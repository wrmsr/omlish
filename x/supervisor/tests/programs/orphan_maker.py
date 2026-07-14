# ruff: noqa: UP006 UP007 UP045
"""
Spawns a child process then exits, leaving orphan.

Usage: python orphan_maker.py [child_duration_seconds]
"""
import os
import sys
import time

from .helpers import log


##


def main() -> None:
    child_duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    log(f'Started orphan_maker pid={os.getpid()}')

    pid = os.fork()

    if pid == 0:
        # Child process - will become orphan
        log(f'Child started pid={os.getpid()} parent={os.getppid()}')
        time.sleep(child_duration)
        log(f'Child exiting pid={os.getpid()} parent={os.getppid()}')
        sys.exit(0)

    else:
        # Parent - exit immediately
        log(f'Parent spawned child pid={pid}, exiting immediately')
        sys.exit(0)


if __name__ == '__main__':
    main()
