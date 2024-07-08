"""
Base:
 - start / restart / stop processes
 - dynamic config reload, reconciling cfg changes to running procs
 - act as pid1 in docker
 - deathsig or equiv - no zombies, if at all possible...

Maybe:
 - log redirection

Stretch:
 - dynamic code reload / re-exec, holding child procs / fds


lookit:
 - https://github.com/python-trio/trio/issues/927
 - https://github.com/oremanj/trio-monitor
 - https://bugs.python.org/issue39060


==


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
import io
import logging
import signal  # noqa
import sys
import threading
import traceback
import typing as ta

from omlish import logs
import anyio.abc


log = logging.getLogger(__name__)


@dc.dataclass(frozen=True)
class ProcessConfig:
    name: str
    cmd: ta.Sequence[str]
    restart: bool = True


class Process:
    def __init__(self, cfg: ProcessConfig) -> None:
        super().__init__()
        self._cfg = cfg

        self._proc: anyio.abc.Process | None = None

    @property
    def name(self) -> str:
        return self._cfg.name

    async def run(self) -> None:
        while True:
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
            if not self._cfg.restart:
                log.debug(f'process {self.name}={proc.pid} not restarting')
            else:
                log.debug(f'process {self.name}={proc.pid} restarting')


def dump(out):
    cthr = threading.current_thread()
    thrs_by_tid = {t.ident: t for t in threading.enumerate()}

    buf = io.StringIO()
    for tid, fr in sys._current_frames().items():  # noqa
        if tid == cthr.ident:
            continue

        try:
            thr = thrs_by_tid[tid]
        except KeyError:
            thr_rpr = repr(tid)
        else:
            thr_rpr = repr(thr)

        tb = traceback.format_stack(fr)

        buf.write(f'{thr_rpr}\n')
        buf.write('\n'.join(l.strip() for l in tb))
        buf.write('\n\n')

    out.write(buf.getvalue())


async def _a_main():
    pcs = [
        ProcessConfig('waiter-3', ['sleep', '3']),
        ProcessConfig('waiter-5', ['sleep', '5']),
        ProcessConfig('waiter-60', ['sleep', '60']),
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

    async def thread_dumper() -> None:
        while True:
            await anyio.sleep(2)
            dump(sys.stderr)

    async with anyio.create_task_group() as tg:
        tg.start_soon(thread_dumper)
        await tg.start(inner)
        for p in ps:
            tg.start_soon(p.run)


if __name__ == '__main__':
    logs.configure_standard_logging('DEBUG')

    anyio.run(_a_main, backend='trio')
