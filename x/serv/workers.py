import asyncio
import logging
import platform
import random
import signal
import typing as ta

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


async def worker_serve(
        app: AppWrapper,
        config: Config,
        *,
        sockets: ta.Optional[Sockets] = None,
        shutdown_trigger: ta.Optional[ta.Callable[..., ta.Awaitable]] = None,
) -> None:
    loop = asyncio.get_event_loop()

    if shutdown_trigger is None:
        signal_event = asyncio.Event()

        def _signal_handler(*_: ta.Any) -> None:  # noqa: N803
            signal_event.set()

        for signal_name in {"SIGINT", "SIGTERM", "SIGBREAK"}:
            if hasattr(signal, signal_name):
                try:
                    loop.add_signal_handler(getattr(signal, signal_name), _signal_handler)
                except NotImplementedError:
                    # Add signal handler may not be implemented on Windows
                    signal.signal(getattr(signal, signal_name), _signal_handler)

        shutdown_trigger = signal_event.wait

    lifespan = Lifespan(app, config, loop)

    lifespan_task = loop.create_task(lifespan.handle_lifespan())
    await lifespan.wait_for_startup()
    if lifespan_task.done():
        exception = lifespan_task.exception()
        if exception is not None:
            raise exception

    if sockets is None:
        sockets = create_sockets(config)

    max_requests = None
    if config.max_requests is not None:
        max_requests = config.max_requests + random.randint(0, config.max_requests_jitter)
    context = WorkerContext(max_requests)
    server_tasks: set[asyncio.Task] = set()

    async def _server_callback(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        nonlocal server_tasks

        task = asyncio.current_task(loop)
        server_tasks.add(task)
        task.add_done_callback(server_tasks.discard)
        await TCPServer(app, loop, config, context, reader, writer)

    servers = []

    for sock in sockets.insecure_sockets:
        if config.workers > 1 and platform.system() == "Windows":
            sock = share_socket(sock)

        servers.append(
            await asyncio.start_server(_server_callback, backlog=config.backlog, sock=sock)
        )
        bind = repr_socket_addr(sock.family, sock.getsockname())
        log.info(f"Running on http://{bind} (CTRL + C to quit)")

    try:
        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(raise_shutdown(shutdown_trigger))
            task_group.create_task(raise_shutdown(context.terminate.wait))
    except BaseExceptionGroup as error:
        _, other_errors = error.split((ShutdownError, KeyboardInterrupt))
        if other_errors is not None:
            raise other_errors
    except (ShutdownError, KeyboardInterrupt):
        pass
    finally:
        await context.terminated.set()

        for server in servers:
            server.close()
            await server.wait_closed()

        try:
            gathered_server_tasks = asyncio.gather(*server_tasks)
            await asyncio.wait_for(gathered_server_tasks, config.graceful_timeout)
        except asyncio.TimeoutError:
            pass
        finally:
            # Retrieve the Gathered Tasks Cancelled Exception, to
            # prevent a warning that this hasn't been done.
            gathered_server_tasks.exception()

            await lifespan.wait_for_shutdown()
            lifespan_task.cancel()
            await lifespan_task


