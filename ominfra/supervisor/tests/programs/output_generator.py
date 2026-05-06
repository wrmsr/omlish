# ruff: noqa: UP006 UP007 UP045
"""
Writes predictable output to stdout/stderr.

Usage: python output_generator.py [num_lines] [interval_seconds] [stderr_ratio]
"""
import os
import sys
import time

from .helpers import err
from .helpers import log


def main():
    num_lines = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    stderr_ratio = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2  # fraction to stderr

    log(f'Started output_generator: lines={num_lines} interval={interval}s pid={os.getpid()}')

    for i in range(num_lines):
        if i % int(1 / stderr_ratio) == 0:
            err(f'STDERR line {i}')
        else:
            log(f'STDOUT line {i}')

        time.sleep(interval)

    log('Output generation complete')
    sys.exit(0)


if __name__ == '__main__':
    main()
