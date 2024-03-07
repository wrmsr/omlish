#!/usr/bin/env python3
# @standalone
import contextlib
import os
import signal
import subprocess
import sys
import time


@contextlib.contextmanager
def start(cmd, *, cwd=None, env=None, timeout=None):
    proc = subprocess.Popen([sys.executable, __file__, cmd], cwd=cwd, env=env)
    try:
        yield
    finally:
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout)


def _main():
    [cmd] = sys.argv[1:]

    def signal_handler(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while os.getppid() != 1:
        time.sleep(1)

    sys.stderr.write(f'timebomb running: {cmd}\n')
    os.system(cmd)


if __name__ == '__main__':
    _main()
