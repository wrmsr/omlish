import os
import sys


def reparent_process(
        *,
        no_close_stdio: bool = False,
) -> None:
    if (pid := os.fork()):  # noqa
        sys.exit(0)
        raise RuntimeError('Unreachable')  # noqa

    os.setsid()

    if (pid := os.fork()):  # noqa
        sys.exit(0)

    if not no_close_stdio:
        rn_fd = os.open('/dev/null', os.O_RDONLY)
        os.dup2(rn_fd, 0)
        os.close(rn_fd)

        wn_fd = os.open('/dev/null', os.O_WRONLY)
        os.dup2(wn_fd, 1)
        os.dup2(wn_fd, 2)
        os.close(wn_fd)

    sys.stdout.flush()
    sys.stderr.flush()
