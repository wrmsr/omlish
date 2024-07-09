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
  - yeesh. punt, treat like uninterrupted code flips? but who was flip??
   - https://github.com/python/cpython/issues/94597
   - https://github.com/python/cpython/blob/15d48aea02099ffc5bdc5511cc53ced460cb31b9/Lib/asyncio/unix_events.py#L845
    - < https://github.com/python/cpython/blob/15d48aea02099ffc5bdc5511cc53ced460cb31b9/Lib/asyncio/base_subprocess.py#L39
    - < https://github.com/python/cpython/blob/15d48aea02099ffc5bdc5511cc53ced460cb31b9/Lib/asyncio/unix_events.py#L203
    - < https://github.com/python/cpython/blob/15d48aea02099ffc5bdc5511cc53ced460cb31b9/Lib/asyncio/base_events.py#L1755
    - < https://github.com/python/cpython/blob/15d48aea02099ffc5bdc5511cc53ced460cb31b9/Lib/asyncio/subprocess.py#L218
   - https://github.com/python-trio/trio/blob/72f5931b66e413f6c32c4614f9bd24ca8eeae834/src/trio/_subprocess.py#L157

Lookit:
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

"""  # noqa
import dataclasses as dc
import io
import logging
import signal  # noqa
import sys
import threading
import traceback
import typing as ta

from omlish import lang
from omlish import logs
import anyio.abc
import anyio.streams.memory


log = logging.getLogger(__name__)


@dc.dataclass(frozen=True)
class ProcessConfig:
    name: str
    cmd: ta.Sequence[str]
    restart: bool = True


T = ta.TypeVar('T')


def split_memory_object_streams(
        *args: anyio.create_memory_object_stream[T],
) -> tuple[
    anyio.streams.memory.MemoryObjectSendStream[T],
    anyio.streams.memory.MemoryObjectReceiveStream[T],
]:
    [tup] = args  # type: ignore
    return tup  # type: ignore


async def gather(*funcs: ta.Callable[..., ta.Awaitable[T]], take_first: bool = False) -> list[lang.Maybe[T]]:
    results = [lang.empty()] * len(funcs)

    async def inner(func, i):
        results[i] = lang.just(await func())
        if take_first:
            tg.cancel_scope.cancel()

    async with anyio.create_task_group() as tg:
        for i, func in enumerate(funcs):
            tg.start_soon(inner, func, i)

    return results


class Process:
    def __init__(self, cfg: ProcessConfig) -> None:
        super().__init__()
        self._cfg = cfg

        self._proc: anyio.abc.Process | None = None
        self._mbox_send, self._mbox_recv = split_memory_object_streams(anyio.create_memory_object_stream[ta.Any]())

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

                    while True:
                        glst = await gather(
                            self._mbox_recv.receive,
                            proc.wait,
                            take_first=True,
                        )

                        if glst[0].present:
                            log.debug(f'process {self.name}={proc.pid} got message: {glst[0].must()}')

                        if glst[1].present:
                            log.debug(f'process {self.name}={proc.pid} exited')
                            break

                except anyio.get_cancelled_exc_class():
                    log.debug(f'process {self.name}={proc.pid} cancelled')
                    raise

            log.debug(f'process {self.name}={proc.pid} done')

            if not self._cfg.restart:
                log.debug(f'process {self.name}={proc.pid} not restarting')
            else:
                log.debug(f'process {self.name}={proc.pid} restarting')


def dump(out):
    thrs_by_tid = {t.ident: t for t in threading.enumerate()}

    buf = io.StringIO()
    for tid, fr in sys._current_frames().items():  # noqa
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

        print('messaging')
        for p in ps:
            await p._mbox_send.send(f'hi process {p.name}')  # noqa

        await anyio.sleep(10)

        print('canceling')
        tg.cancel_scope.cancel()

    async def thread_dumper() -> None:
        while True:
            await anyio.sleep(2)
            dump(sys.stderr)

    async with anyio.create_task_group() as tg:
        # tg.start_soon(thread_dumper)

        await tg.start(inner)

        for p in ps:
            tg.start_soon(p.run)


if __name__ == '__main__':
    backend = 'asyncio'
    # backend = 'trio'

    if backend == 'asyncio':
        if sys.platform == 'linux':
            import asyncio
            asyncio.get_event_loop_policy().set_child_watcher(asyncio.unix_events.PidfdChildWatcher())

    logs.configure_standard_logging('DEBUG')

    anyio.run(
        _a_main,
        backend=backend,
    )
