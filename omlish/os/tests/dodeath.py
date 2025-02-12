import os
import sys
import time

from ..death import ForkAwarePipeDeathpact  # noqa
from ..death import PipeDeathpact
from ..files import is_fd_open


def _main() -> None:
    def fd_info(fd: int | None) -> str:
        return f'{fd}, open={is_fd_open(fd) if fd is not None else "-"}'

    reparent = True

    pdp_cls: type[PipeDeathpact] = PipeDeathpact  # noqa
    # pdp_cls = ForkAwarePipeDeathpact

    try:
        with pdp_cls() as pdp:
            def print_pdp_infp() -> None:
                print(f'{os.getpid()=} {fd_info(pdp._rfd)=} {fd_info(pdp._wfd)=}', file=sys.stderr)  # noqa

            print_pdp_infp()

            if not (child_pid := os.fork()):  # noqa
                if reparent:
                    print(f'child process {os.getpid()} reparenting', file=sys.stderr)
                    print_pdp_infp()

                    if os.fork():
                        sys.exit(0)

                for i in range(10, 0, -1):
                    print(f'child process {os.getpid()} polling {i}', file=sys.stderr)
                    print_pdp_infp()

                    pdp.poll()
                    time.sleep(1.)

            else:
                for i in range(3, 0, -1):
                    print(f'parent process {os.getpid()} sleeping {i}', file=sys.stderr)
                    print_pdp_infp()

                    time.sleep(1.)

    finally:
        print(f'process {os.getpid()} exiting', file=sys.stderr)


if __name__ == '__main__':
    _main()
