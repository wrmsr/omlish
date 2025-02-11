import argparse
import fcntl
import os
import signal
import tempfile
import time


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('--fork', action='store_true')
    args = parser.parse_args()

    if (file := args.file) is None:
        fd, file = tempfile.mkstemp()
        os.set_inheritable(fd, True)
    else:
        fd = os.open(file, os.O_RDWR | os.O_CREAT)
    print(f'file: {file}')

    print(f'parent: {os.getpid()}')
    child_pid = None
    if args.fork and not (child_pid := os.fork()):
        while True:
            time.sleep(60 * 60)
        raise RuntimeError  # noqa
    else:
        if child_pid is not None:
            print(f'child: {child_pid}')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        input()
        if child_pid is not None:
            os.kill(child_pid, signal.SIGTERM)


if __name__ == '__main__':
    _main()
