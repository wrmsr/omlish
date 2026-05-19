import functools
import multiprocessing as mp
import multiprocessing.connection
import multiprocessing.context
import multiprocessing.synchronize
import pickle
import platform
import signal
import time
import typing as ta

import anyio

from .config import Config
from .default import serve
from .sockets import Sockets
from .sockets import create_sockets
from .types import AsgiFramework
from .types import wrap_app


##


async def check_multiprocess_shutdown_event(
        shutdown_event: mp.synchronize.Event,
        sleep: ta.Callable[[float], ta.Awaitable[ta.Any]],
) -> None:
    while True:
        if shutdown_event.is_set():
            return
        await sleep(0.1)


def _multiprocess_serve(
        app: AsgiFramework,
        config: Config,
        sockets: Sockets | None = None,
        shutdown_event: mp.synchronize.Event | None = None,
) -> None:
    if sockets is not None:
        for sock in sockets.insecure_sockets:
            sock.listen(config.backlog)

    shutdown_trigger = None
    if shutdown_event is not None:
        shutdown_trigger = functools.partial(check_multiprocess_shutdown_event, shutdown_event, anyio.sleep)

    anyio.run(
        functools.partial(
            serve,
            wrap_app(app),
            config,
            sockets=sockets,
            shutdown_trigger=shutdown_trigger,
        ),
        # backend='trio',
    )


def serve_multiprocess(
        app: AsgiFramework,
        config: Config,
) -> int:
    sockets = create_sockets(config)

    exitcode = 0
    ctx = mp.get_context('spawn')

    active = True
    shutdown_event = ctx.Event()

    def shutdown(*args: ta.Any) -> None:
        shutdown_event.set()
        nonlocal active
        active = False

    processes: list[mp.Process] = []
    while active:
        # Ignore SIGINT before creating the processes, so that they inherit the signal handling. This means that the
        # shutdown function controls the shutdown.
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        _populate(
            processes,
            app,
            config,
            _multiprocess_serve,
            sockets,
            shutdown_event,
            ctx,
        )

        for signal_name in ('SIGINT', 'SIGTERM', 'SIGBREAK'):
            if hasattr(signal, signal_name):
                signal.signal(getattr(signal, signal_name), shutdown)

        mp.connection.wait(process.sentinel for process in processes)

        exitcode = _join_exited(processes)
        if exitcode != 0:
            shutdown_event.set()
            active = False

    for process in processes:
        process.terminate()

    exitcode = _join_exited(processes) if exitcode != 0 else exitcode

    for sock in sockets.insecure_sockets:
        sock.close()

    return exitcode


def _populate(
        processes: list[mp.Process],
        app: AsgiFramework,
        config: Config,
        worker_func: ta.Callable,
        sockets: Sockets,
        shutdown_event: mp.synchronize.Event,
        ctx: mp.context.BaseContext,
) -> None:
    num_workers = config.workers or 1
    if num_workers < 0:
        num_workers = mp.cpu_count()
    for _ in range(num_workers - len(processes)):
        process = ctx.Process(  # type: ignore
            target=worker_func,
            kwargs={
                'app': app,
                'config': config,
                'shutdown_event': shutdown_event,
                'sockets': sockets,
            },
        )
        process.daemon = True
        try:
            process.start()
        except pickle.PicklingError as error:
            raise RuntimeError(
                'Cannot pickle the config, see https://docs.python.org/3/library/pickle.html#pickle-picklable',
                # noqa: E501
            ) from error
        processes.append(process)
        if platform.system() == 'Windows':
            time.sleep(0.1)


def _join_exited(processes: list[mp.Process]) -> int:
    exitcode = 0
    for index in reversed(range(len(processes))):
        worker = processes[index]
        if worker.exitcode is not None:
            worker.join()
            exitcode = worker.exitcode if exitcode == 0 else exitcode
            del processes[index]

    return exitcode
