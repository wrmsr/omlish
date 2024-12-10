import argparse
import os
import sys


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--fork', action='store_true')
    parser.add_argument('--reexec')
    parser.add_argument('--setpgid', action='store_true')
    args = parser.parse_args()

    def inner():
        if args.reexec:
            os.execl(
                sys.executable,
                sys.executable,
                __file__,
                *args.reexec.split(' '),
            )

        if args.setpgid:
            os.setpgid(0, 0)

    if args.fork:
        if not (cpid := os.fork()):
            inner()
        else:
            os.waitpid(cpid, 0)


if __name__ == '__main__':
    _main()
