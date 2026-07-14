import os
import subprocess
import sys
import typing as ta

from ..forkhooks import ForkHook
from ..forkhooks import get_fork_depth


##


class _PrintForkHook(ForkHook, install=True):
    _print_queue: ta.ClassVar[list[str]] = []

    @classmethod
    def print_queued(cls) -> None:
        for s in cls._print_queue:
            print(s, file=sys.stderr)
        cls._print_queue.clear()

    @classmethod
    def _queue_print(cls, name: str) -> None:
        cls._print_queue.append(f'{name}: {os.getpid()=} {get_fork_depth()=}')

    @classmethod
    def _before_fork(cls) -> None:
        cls._queue_print('before_fork')

    @classmethod
    def _after_fork_in_parent(cls) -> None:
        cls._queue_print('fork_in_parent')

    @classmethod
    def _after_fork_in_child(cls) -> None:
        cls._queue_print('fork_in_child')


def _main() -> None:
    print(f'parent: {os.getpid()=} {get_fork_depth()=}', file=sys.stderr)

    # from ..forkhooks import _ForkHookManager  # noqa
    # print(_ForkHookManager._priority_ordered_hooks, file=sys.stderr)  # noqa
    # print(list(_ForkHookManager._hooks_by_key.values()), file=sys.stderr)  # noqa

    def pre_exec():
        _PrintForkHook.print_queued()
        print(f'pre_exec: {os.getpid()=} {get_fork_depth()=}', file=sys.stderr)

    with subprocess.Popen(
        ['true'],
        preexec_fn=pre_exec,  # noqa
    ) as proc:
        proc.wait()

    subprocess.check_call(
        ['true'],
        preexec_fn=pre_exec,
    )


if __name__ == '__main__':
    _main()
