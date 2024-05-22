import errno
import logging
import functools
import os
import platform
import random
import signal  # noqa
import typing as ta

import anyio
import anyio.abc

from .config import Config
from .lifespans import Lifespan
from .sockets import Sockets
from .sockets import create_sockets
from .sockets import repr_socket_addr
from .sockets import share_socket
from .tcpserver import TCPServer
from .types import AppWrapper
from .workercontext import ShutdownError
from .workercontext import WorkerContext


log = logging.getLogger(__name__)


async def raise_shutdown(shutdown_event: ta.Callable[..., ta.Awaitable]) -> None:
    await shutdown_event()
    raise ShutdownError()


# Errors that accept(2) can return, and which indicate that the system is overloaded
ACCEPT_CAPACITY_ERRNOS = {
    errno.EMFILE,
    errno.ENFILE,
    errno.ENOMEM,
    errno.ENOBUFS,
}


async def _run_handler(stream, handler) -> None:
    try:
        await handler(stream)
    finally:
        await anyio.aclose_forcefully(stream)


SLEEP_TIME = 0.100


async def _serve_one_listener(
        listener,
        handler_nursery,
        handler,
) -> ta.NoReturn:
    async with listener:
        while True:
            try:
                stream = await listener.accept()
            except OSError as exc:
                if exc.errno in ACCEPT_CAPACITY_ERRNOS:
                    log.error(
                        "accept returned %s (%s); retrying in %s seconds",
                        errno.errorcode[exc.errno],
                        os.strerror(exc.errno),
                        SLEEP_TIME,
                        exc_info=True,
                    )
                    await anyio.sleep(SLEEP_TIME)
                else:
                    raise
            else:
                handler_nursery.start_soon(_run_handler, stream, handler)


async def serve_listeners(
        handler,
        listeners,
        *,
        handler_nursery=None,
        task_status=anyio.TASK_STATUS_IGNORED,
) -> ta.NoReturn:
    async with anyio.create_task_group() as nursery:
        if handler_nursery is None:
            handler_nursery = nursery
        for listener in listeners:
            nursery.start_soon(_serve_one_listener, listener, handler_nursery, handler)
        # The listeners are already queueing connections when we're called, but we wait until the end to call started()
        # just in case we get an error or whatever.
        task_status.started(listeners)

    raise RuntimeError('unreachable')

async def worker_serve(
        app: AppWrapper,
        config: Config,
        *,
        sockets: ta.Optional[Sockets] = None,
        shutdown_trigger: ta.Optional[ta.Callable[..., ta.Awaitable[None]]] = None,
        task_status: anyio.abc.TaskStatus[None] = anyio.TASK_STATUS_IGNORED,
) -> None:
    # if shutdown_trigger is None:
    #     signal_event = asyncio.Event()
    #
    #     def _signal_handler(*_: ta.Any) -> None:  # noqa: N803
    #         signal_event.set()
    #
    #     for signal_name in {"SIGINT", "SIGTERM", "SIGBREAK"}:
    #         if hasattr(signal, signal_name):
    #             try:
    #                 loop.add_signal_handler(getattr(signal, signal_name), _signal_handler)
    #             except NotImplementedError:
    #                 # Add signal handler may not be implemented on Windows
    #                 signal.signal(getattr(signal, signal_name), _signal_handler)
    #
    #     shutdown_trigger = signal_event.wait

    lifespan = Lifespan(app, config)
    max_requests = None
    if config.max_requests is not None:
        max_requests = config.max_requests + random.randint(0, config.max_requests_jitter)
    context = WorkerContext(max_requests)

    async with anyio.create_task_group() as lifespan_nursery:
        await lifespan_nursery.start(lifespan.handle_lifespan)
        await lifespan.wait_for_startup()

        async with anyio.create_task_group() as server_nursery:
            if sockets is None:
                sockets = create_sockets(config)
                for sock in sockets.insecure_sockets:
                    if config.workers > 1 and platform.system() == "Windows":
                        sock = share_socket(sock)
                    sock.listen(config.backlog)

            listeners = []
            binds = []

            for sock in sockets.insecure_sockets:
                listeners.append(anyio._core._eventloop.get_async_backend().create_tcp_listener(sock))
                bind = repr_socket_addr(sock.family, sock.getsockname())
                binds.append(f"http://{bind}")
                log.info(f"Running on http://{bind} (CTRL + C to quit)")

            task_status.started(binds)
            try:
                async with anyio.create_task_group() as nursery:
                    if shutdown_trigger is not None:
                        nursery.start_soon(raise_shutdown, shutdown_trigger)
                    nursery.start_soon(raise_shutdown, context.terminate.wait)

                    nursery.start_soon(
                        functools.partial(
                            serve_listeners,
                            functools.partial(TCPServer, app, config, context),
                            listeners,
                            handler_nursery=server_nursery,
                        ),
                    )

                    await anyio.sleep_forever()
            except BaseExceptionGroup as error:
                _, other_errors = error.split((ShutdownError, KeyboardInterrupt))
                if other_errors is not None:
                    raise other_errors
            finally:
                await context.terminated.set()
                server_nursery.cancel_scope.deadline = anyio.current_time() + config.graceful_timeout

        await lifespan.wait_for_shutdown()
        lifespan_nursery.cancel_scope.cancel()
