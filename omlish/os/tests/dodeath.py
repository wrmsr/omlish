import functools  # noqa
import os
import sys
import time
import typing as ta

from .. import deathpacts
from ..temp import make_temp_file  # noqa
from ..files import is_fd_open


def _main() -> None:
    def fd_info(fd: int | None) -> str:
        return f'{fd}, open={is_fd_open(fd) if fd is not None else "-"}'

    reparent = True

    dp_fac: ta.Callable[[], deathpacts.Deathpact]
    # dp_fac = deathpacts.PipeDeathpact
    # dp_fac = deathpacts.ForkAwarePipeDeathpact
    dp_fac = functools.partial(deathpacts.HeartbeatFileDeathpact, make_temp_file(), ttl_s=2.)

    try:
        with dp_fac() as dp:
            def print_dp_info() -> None:
                if isinstance(dp, deathpacts.PipeDeathpact):
                    print(f'{os.getpid()=} {fd_info(dp._rfd)=} {fd_info(dp._wfd)=}', file=sys.stderr)  # noqa
                elif isinstance(dp, deathpacts.HeartbeatFileDeathpact):
                    print(f'{os.getpid()=} {dp.read()=}', file=sys.stderr)  # noqa
                else:
                    raise TypeError(dp)

            print_dp_info()

            if not (child_pid := os.fork()):  # noqa
                if reparent:
                    print(f'child process {os.getpid()} reparenting', file=sys.stderr)
                    print_dp_info()

                    if os.fork():
                        sys.exit(0)

                for i in range(10, 0, -1):
                    print(f'child process {os.getpid()} polling {i}', file=sys.stderr)
                    print_dp_info()

                    dp.poll()
                    time.sleep(1.)

            else:
                for i in range(3, 0, -1):
                    print(f'parent process {os.getpid()} sleeping {i}', file=sys.stderr)
                    print_dp_info()

                    if isinstance(dp, deathpacts.HeartbeatFileDeathpact):
                        dp.update()

                    time.sleep(1.)

                print(f'parent process {os.getpid()} closing pact')
                dp.close()

                for i in range(3, 0, -1):
                    print(f'parent process {os.getpid()} sleeping {i}', file=sys.stderr)
                    print_dp_info()

                    time.sleep(1.)

    finally:
        print(f'process {os.getpid()} exiting', file=sys.stderr)


if __name__ == '__main__':
    _main()
