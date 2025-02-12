import os
import sys
import time

from ..death import PipeDeathpact


def _main() -> None:
    reparent = False

    try:
        with PipeDeathpact() as pdp:
            if not (child_pid := os.fork()):  # noqa
                if reparent:
                    raise NotImplementedError

                while True:
                    print(f'child process {os.getpid()} polling', file=sys.stderr)
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
