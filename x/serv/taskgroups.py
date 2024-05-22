import logging
import types
import typing as ta

import anyio
import anyio.abc

from .config import Config
from .types import ASGIReceiveCallable
from .types import ASGIReceiveEvent
from .types import ASGISendEvent
from .types import AppWrapper
from .types import Scope


log = logging.getLogger(__name__)


async def _handle(
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
    except anyio.get_cancelled_exc_class():
        raise
    except BaseExceptionGroup as error:
        _, other_errors = error.split(anyio.get_cancelled_exc_class())
        if other_errors is not None:
            log.exception("Error in ASGI Framework")
            await send(None)
        else:
            raise
    except Exception:
        log.exception("Error in ASGI Framework")
    finally:
        await send(None)


class TaskGroup:
    def __init__(self) -> None:
        super().__init__()
        self._nursery: ta.Optional[ta.Any] = None
        self._nursery_manager: ta.Optional[anyio.abc.TaskGroup] = None

    async def spawn_app(
            self,
            app: AppWrapper,
            config: Config,
            scope: Scope,
            send: ta.Callable[[ta.Optional[ASGISendEvent]], ta.Awaitable[None]],
    ) -> ta.Callable[[ASGIReceiveEvent], ta.Awaitable[None]]:
        app_send_channel, app_receive_channel = anyio.create_memory_object_stream[bytes](config.max_app_queue_size)
        self._nursery.start_soon(
            _handle,
            app,
            config,
            scope,
            app_receive_channel.receive,
            send,
            None,  # trio.to_thread.run_sync,
            None,  # trio.from_thread.run,
        )
        return app_send_channel.send

    def spawn(self, func: ta.Callable, *args: ta.Any) -> None:
        self._nursery.start_soon(func, *args)

    async def __aenter__(self) -> anyio.abc.TaskGroup:
        self._nursery_manager = anyio.create_task_group()
        self._nursery = await self._nursery_manager.__aenter__()
        return self

    async def __aexit__(self, exc_type: type, exc_value: BaseException, tb: types.TracebackType) -> None:
        await self._nursery_manager.__aexit__(exc_type, exc_value, tb)
        self._nursery_manager = None
        self._nursery = None
