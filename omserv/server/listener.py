import errno
import functools
import logging
import os
import random
import signal  # noqa
import typing as ta

import anyio
import anyio.abc

from .config import Config
from .lifespans import Lifespan
from .server import ServerFactory
from .sockets import Sockets
from .sockets import create_sockets
from .sockets import repr_socket_addr
from .types import AppWrapper
from .types import AsgiFramework
from .types import wrap_app
from .workercontext import ShutdownError
from .workercontext import WorkerContext


log = logging.getLogger(__name__)


async def raise_shutdown(shutdown_event: ta.Callable[..., ta.Awaitable]) -> None:
    await shutdown_event()
    raise ShutdownError


# Errors that accept(2) can return, and which indicate that the system is overloaded
ACCEPT_CAPACITY_ERRNOS = {
    errno.EMFILE,
    errno.ENFILE,
    errno.ENOMEM,
    errno.ENOBUFS,
}


async def _run_handler(
        stream: anyio.abc.SocketStream,
        handler: ta.Callable[[anyio.abc.SocketStream], ta.Awaitable],
) -> None:
    try:
        await handler(stream)
    finally:
        await anyio.aclose_forcefully(stream)


SLEEP_TIME = .1


async def _serve_one_listener(
        listener: anyio.abc.SocketListener,
        handler_task_group: anyio.abc.TaskGroup,
        handler: ta.Callable[[anyio.abc.SocketStream], ta.Awaitable],
) -> ta.NoReturn:
    async with listener:
        while True:
            try:
                stream = await listener.accept()
            except OSError as exc:
                if exc.errno in ACCEPT_CAPACITY_ERRNOS:
                    log.exception(
                        'accept returned %s (%s); retrying in %s seconds',
                        errno.errorcode[exc.errno],
                        os.strerror(exc.errno),
                        SLEEP_TIME,
                    )
                    await anyio.sleep(SLEEP_TIME)
                else:
                    raise
            else:
                handler_task_group.start_soon(_run_handler, stream, handler)


async def serve_listeners(
        handler: ta.Callable[[anyio.abc.SocketStream], ta.Awaitable],
        listeners: ta.Iterable[anyio.abc.SocketListener],
        *,
        handler_task_group: anyio.abc.TaskGroup | None = None,
        task_status: anyio.abc.TaskStatus[ta.Iterable[anyio.abc.SocketListener]] = anyio.TASK_STATUS_IGNORED,
) -> ta.NoReturn:
    async with anyio.create_task_group() as task_group:
        if handler_task_group is None:
            handler_task_group = task_group
        for listener in listeners:
            task_group.start_soon(_serve_one_listener, listener, handler_task_group, handler)
        # The listeners are already queueing connections when we're called, but we wait until the end to call started()
        # just in case we get an error or whatever.
        task_status.started(listeners)

    raise RuntimeError('unreachable')


async def _install_signal_handler(
        tg: anyio.abc.TaskGroup,
) -> ta.Callable[..., ta.Awaitable[None]] | None:
    signal_event = anyio.Event()

    sigs = [
        getattr(signal, signal_name)
        for signal_name in ('SIGINT', 'SIGTERM', 'SIGBREAK')
        if hasattr(signal, signal_name)
    ]

    if not sigs:
        return None

    async def _handler(*, task_status=anyio.TASK_STATUS_IGNORED):
        with anyio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
            task_status.started()
            async for signum in signals:
                if signum == signal.SIGINT:
                    print('Ctrl+C pressed!')
                else:
                    print('Terminated!')

                signal_event.set()
                return

    await tg.start(_handler)
    return signal_event.wait


class Listener:
    def __init__(
            self,
            *,
            server_factory: ServerFactory,
    ) -> None:
        super().__init__()

        self._server_factory = server_factory

    async def listen(
            self,
            app: AsgiFramework | AppWrapper,
            config: Config,
            *,
            sockets: Sockets | None = None,
            shutdown_trigger: ta.Callable[..., ta.Awaitable[None]] | None = None,
            handle_shutdown_signals: bool = False,
            task_status: anyio.abc.TaskStatus[ta.Sequence[str]] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        app = wrap_app(app)

        lifespan = Lifespan(app, config)
        max_requests = None
        if config.max_requests is not None:
            max_requests = config.max_requests + random.randint(0, config.max_requests_jitter)
        context = WorkerContext(max_requests)

        async with anyio.create_task_group() as lifespan_task_group:
            if shutdown_trigger is None and handle_shutdown_signals:
                shutdown_trigger = await _install_signal_handler(lifespan_task_group)

            await lifespan_task_group.start(lifespan.handle_lifespan)
            await lifespan.wait_for_startup()

            async with anyio.create_task_group() as server_task_group:
                if sockets is None:
                    sockets = create_sockets(config)
                    for sock in sockets.insecure_sockets:
                        sock.listen(config.backlog)

                listeners = []
                binds = []

                for sock in sockets.insecure_sockets:
                    listeners.append(anyio._core._eventloop.get_async_backend().create_tcp_listener(sock))  # noqa
                    bind = repr_socket_addr(sock.family, sock.getsockname())
                    binds.append(f'http://{bind}')
                    log.info('Running on http://%s (CTRL + C to quit)', bind)

                task_status.started(binds)
                try:
                    async with anyio.create_task_group() as task_group:
                        if shutdown_trigger is not None:
                            task_group.start_soon(raise_shutdown, shutdown_trigger)
                        task_group.start_soon(raise_shutdown, context.terminate.wait)

                        task_group.start_soon(
                            functools.partial(
                                serve_listeners,
                                functools.partial(self._server_factory, app, context),
                                listeners,
                                handler_task_group=server_task_group,
                            ),
                        )

                        await anyio.sleep_forever()
                except BaseExceptionGroup as error:
                    _, other_errors = error.split((ShutdownError, KeyboardInterrupt))  # noqa
                    if other_errors is not None:
                        raise other_errors  # noqa
                finally:
                    await context.terminated.set()
                    server_task_group.cancel_scope.deadline = anyio.current_time() + config.graceful_timeout

            await lifespan.wait_for_shutdown()
            lifespan_task_group.cancel_scope.cancel()
