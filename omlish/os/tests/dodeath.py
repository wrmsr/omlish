import errno
import fcntl
import os
import sys
import time

from ..death import PipeDeathpact
from ..files import is_fd_open


def _main() -> None:
    reparent = False

    try:
        with PipeDeathpact() as pdp:
            print(is_fd_open(pdp._rfd))
            print(is_fd_open(pdp._wfd))
            print(is_fd_open(420))

            if not (child_pid := os.fork()):  # noqa
                print(is_fd_open(pdp._rfd))
                print(is_fd_open(pdp._wfd))
                print(is_fd_open(420))

                if reparent:
                    raise NotImplementedError

                for i in range(10, 0, -1):
                    print(f'child process {os.getpid()} polling {i}', file=sys.stderr)
                    pdp.poll()
                    time.sleep(1.)

            else:
                for i in range(3, 0, -1):
                    print(f'parent process {os.getpid()} sleeping {i}', file=sys.stderr)
                    time.sleep(1.)

    finally:
        print(f'process {os.getpid()} exiting', file=sys.stderr)


if __name__ == '__main__':
    _main()
