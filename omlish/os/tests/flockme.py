import argparse
import fcntl
import os
import signal
import tempfile
import time


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    args = parser.parse_args()

    if (file := args.file) is None:
        fd, file = tempfile.mkstemp()
        os.set_inheritable(fd, True)
    else:
        fd = os.open(file, os.O_RDWR | os.O_CREAT)
    print(f'file: {file}')

    print(f'parent: {os.getpid()}')
    if not (pid := os.fork()):
        while True:
            time.sleep(60 * 60)
    else:
        print(f'child: {pid}')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        input()
        os.kill(pid, signal.SIGTERM)


if __name__ == '__main__':
    _main()
