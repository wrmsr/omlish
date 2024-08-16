import logging
import types
import typing as ta

import anyio
import anyio.abc
import anyio.from_thread
import anyio.to_thread

from omlish import check

from .config import Config
from .debug import handle_error_debug
from .types import AppWrapper
from .types import AsgiReceiveCallable
from .types import AsgiReceiveEvent
from .types import AsgiSendEvent
from .types import Scope


log = logging.getLogger(__name__)


async def _handle(
        app: AppWrapper,
        config: Config,
        scope: Scope,
        receive: AsgiReceiveCallable,
        send: ta.Callable[[AsgiSendEvent | None], ta.Awaitable[None]],
        sync_spawn: ta.Callable,
        call_soon: ta.Callable,
) -> None:
    try:
        await app(
            scope,
            receive,
            send,
            sync_spawn,
            call_soon,
        )

    except anyio.get_cancelled_exc_class():
        raise

    except BaseExceptionGroup as error:
        handle_error_debug(error)

        _, other_errors = error.split(anyio.get_cancelled_exc_class())
        if other_errors is not None:
            log.exception('Error in Asgi Framework')
            await send(None)
        else:
            raise

    except Exception as error:
        handle_error_debug(error)

        log.exception('Error in Asgi Framework')

    finally:
        await send(None)


class TaskSpawner:
    def __init__(self) -> None:
        super().__init__()
        self._task_group: anyio.abc.TaskGroup | None = None

    async def start(
            self,
            func: ta.Callable[..., ta.Awaitable[ta.Any]],
            *args: ta.Any,
    ) -> anyio.CancelScope:
        return await check.not_none(self._task_group).start(func, *args)

    async def spawn_app(
            self,
            app: AppWrapper,
            config: Config,
            scope: Scope,
            send: ta.Callable[[AsgiSendEvent | None], ta.Awaitable[None]],
    ) -> ta.Callable[[AsgiReceiveEvent], ta.Awaitable[None]]:
        app_send_channel, app_receive_channel = anyio.create_memory_object_stream[ta.Any](config.max_app_queue_size)
        check.not_none(self._task_group).start_soon(
            _handle,
            app,
            config,
            scope,
            app_receive_channel.receive,
            send,
            anyio.to_thread.run_sync,
            anyio.from_thread.run,
        )
        return app_send_channel.send

    def spawn(self, func: ta.Callable, *args: ta.Any) -> None:
        check.not_none(self._task_group).start_soon(func, *args)

    async def __aenter__(self) -> ta.Self:
        self._task_group = anyio.create_task_group()
        await self._task_group.__aenter__()
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            tb: types.TracebackType | None,
    ) -> None:
        await check.not_none(self._task_group).__aexit__(exc_type, exc_value, tb)
        self._task_group = None
