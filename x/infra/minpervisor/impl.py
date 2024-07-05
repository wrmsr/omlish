import dataclasses as dc
import signal
import typing as ta

import anyio.abc


@dc.dataclass(frozen=True)
class ProcessConfig:
    name: str
    cmd: ta.Sequence[str]


class Process:
    def __init__(self, cfg: ProcessConfig) -> None:
        super().__init__()
        self._cfg = cfg

        self._proc: anyio.abc.Process | None = None

    async def start(self) -> None:
        self._proc = await anyio.open_process(
            self._cfg.cmd
        )


async def _a_main():
    pcs = [
        ProcessConfig('waiter-0', ['sleep', '60']),
        ProcessConfig('waiter-1', ['sleep', '90']),
    ]

    ps = []
    for pc in pcs:
        p = Process(pc)
        ps.append(p)
        await p.start()

    await anyio.sleep(10)

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


if __name__ == '__main__':
    anyio.run(_a_main)
