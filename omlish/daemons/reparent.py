import os
import sys


def reparent_process() -> None:
    if (pid := os.fork()):  # noqa
        sys.exit(0)

    os.setsid()

    if (pid := os.fork()):  # noqa
        sys.exit(0)

    sys.stdout.flush()
    sys.stderr.flush()
