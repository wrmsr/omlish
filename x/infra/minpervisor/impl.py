"""
- https://github.com/python-trio/trio/issues/927
- https://github.com/oremanj/trio-monitor
- https://bugs.python.org/issue39060

    for p in ps:
        p._proc.send_signal(signal.SIGTERM)

    for p in ps:
        async with anyio.create_task_group() as tg:
            with anyio.move_on_after(3) as scope:
                await p._proc.wait()

            if scope.cancelled_caught:
                p._proc.send_signal(signal.SIGKILL)

                with anyio.move_on_after(3) as scope:
                    await p._proc.wait()

                if scope.cancelled_caught:
                    print('FAILED TO REAP')

"""
import dataclasses as dc
import logging
import signal
import typing as ta

from omlish import logs
import anyio.abc


log = logging.getLogger(__name__)


@dc.dataclass(frozen=True)
class ProcessConfig:
    name: str
    cmd: ta.Sequence[str]


class Process:
    def __init__(self, cfg: ProcessConfig) -> None:
        super().__init__()
        self._cfg = cfg

        self._proc: anyio.abc.Process | None = None

    @property
    def name(self) -> str:
        return self._cfg.name

    async def run(self) -> None:
        log.debug(f'process {self.name} starting')
        proc = await anyio.open_process(
            self._cfg.cmd
        )
        log.debug(f'process {self.name}={proc.pid} started')
        async with proc:
            try:
                log.debug(f'process {self.name}={proc.pid} waiting')
                await proc.wait()
                log.debug(f'process {self.name}={proc.pid} exited')
            except anyio.get_cancelled_exc_class():
                log.debug(f'process {self.name}={proc.pid} cancelled')
                raise
        log.debug(f'process {self.name}={proc.pid} done')


async def _a_main():
    pcs = [
        ProcessConfig('waiter-0', ['sleep', '3']),
        ProcessConfig('waiter-1', ['sleep', '5']),
    ]

    ps = []
    for pc in pcs:
        p = Process(pc)
        ps.append(p)

    async def inner(*, task_status: anyio.abc.TaskStatus) -> None:
        task_status.started()
        await anyio.sleep(10)
        print('canceling')
        tg.cancel_scope.cancel()

    async with anyio.create_task_group() as tg:
        await tg.start(inner)
        for p in ps:
            tg.start_soon(p.run)


if __name__ == '__main__':
    logs.configure_standard_logging('DEBUG')

    anyio.run(_a_main, backend='trio')
