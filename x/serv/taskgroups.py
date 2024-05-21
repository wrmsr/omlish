import asyncio
import functools
import logging
import types
import typing as ta

from .config import Config
from .types import ASGIReceiveCallable
from .types import ASGIReceiveEvent
from .types import ASGISendEvent
from .types import AppWrapper
from .types import Scope


log = logging.getLogger(__name__)


async def _task_group_handle(
        app: AppWrapper,
        config: Config,
        scope: Scope,
        receive: ASGIReceiveCallable,
        send: ta.Callable[[ta.Optional[ASGISendEvent]], ta.Awaitable[None]],
        sync_spawn: ta.Callable,
        call_soon: ta.Callable,
) -> None:
    try:
        await app(scope, receive, send, sync_spawn, call_soon)
    except asyncio.CancelledError:
        raise
    except Exception:
        log.exception("Error in ASGI Framework")
    finally:
        await send(None)


class TaskGroup:
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__()
        self._loop = loop
        self._task_group = asyncio.TaskGroup()

    async def spawn_app(
            self,
            app: AppWrapper,
            config: Config,
            scope: Scope,
            send: ta.Callable[[ta.Optional[ASGISendEvent]], ta.Awaitable[None]],
    ) -> ta.Callable[[ASGIReceiveEvent], ta.Awaitable[None]]:
        app_queue: asyncio.Queue[ASGIReceiveEvent] = asyncio.Queue(config.max_app_queue_size)

        def _call_soon(func: ta.Callable, *args: ta.Any) -> ta.Any:
            future = asyncio.run_coroutine_threadsafe(func(*args), self._loop)
            return future.result()

        self.spawn(
            _task_group_handle,
            app,
            config,
            scope,
            app_queue.get,
            send,
            functools.partial(self._loop.run_in_executor, None),
            _call_soon,
        )
        return app_queue.put

    def spawn(self, func: ta.Callable, *args: ta.Any) -> None:
        self._task_group.create_task(func(*args))

    async def __aenter__(self) -> "TaskGroup":
        await self._task_group.__aenter__()
        return self

    async def __aexit__(self, exc_type: type, exc_value: BaseException, tb: types.TracebackType) -> None:
        await self._task_group.__aexit__(exc_type, exc_value, tb)
