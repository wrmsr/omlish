import logging
import typing as ta

import anyio
import anyio.abc
import anyio.from_thread
import anyio.to_thread

from .config import Config
from .debug import handle_error_debug
from .types import AppWrapper
from .types import AsgiReceiveEvent
from .types import AsgiSendEvent
from .types import LifespanScope
from .types import UnexpectedMessageError


log = logging.getLogger(__name__)


class LifespanTimeoutError(Exception):
    def __init__(self, stage: str) -> None:
        super().__init__(
            f'Timeout whilst awaiting {stage}. Your application may not support the Asgi Lifespan '
            f'protocol correctly, alternatively the {stage}_timeout configuration is incorrect.',
        )


class LifespanFailureError(Exception):
    def __init__(self, stage: str, message: str) -> None:
        super().__init__(f"Lifespan failure in {stage}. '{message}'")


class Lifespan:
    def __init__(self, app: AppWrapper, config: Config) -> None:
        super().__init__()
        self.app = app
        self.config = config
        self.startup = anyio.Event()
        self.shutdown = anyio.Event()
        self.app_send_channel, self.app_receive_channel = anyio.create_memory_object_stream[ta.Any](
            config.max_app_queue_size,
        )
        self.supported = True

    async def handle_lifespan(
            self,
            *,
            task_status: anyio.abc.TaskStatus[ta.Any] = anyio.TASK_STATUS_IGNORED,
    ) -> None:
        task_status.started()
        scope: LifespanScope = {
            'type': 'lifespan',
            'asgi': {'spec_version': '2.0', 'version': '3.0'},
        }

        try:
            await self.app(
                scope,
                self.asgi_receive,
                self.asgi_send,
                anyio.to_thread.run_sync,
                anyio.from_thread.run,
            )
        except (LifespanFailureError, anyio.get_cancelled_exc_class()):
            raise
        except (BaseExceptionGroup, Exception) as error:
            handle_error_debug(error)

            if isinstance(error, BaseExceptionGroup):
                failure_error = error.subgroup(LifespanFailureError)
                if failure_error is not None:
                    # Lifespan failures should crash the server
                    raise failure_error  # noqa
                reraise_error = error.subgroup((LifespanFailureError, anyio.get_cancelled_exc_class()))
                if reraise_error is not None:
                    raise reraise_error  # noqa

            self.supported = False
            if not self.startup.is_set():
                log.warning('Asgi Framework Lifespan error, continuing without Lifespan support')
            elif not self.shutdown.is_set():
                log.exception('Asgi Framework Lifespan error, shutdown without Lifespan support')
            else:
                log.exception('Asgi Framework Lifespan errored after shutdown.')

        finally:
            self.startup.set()
            self.shutdown.set()
            await self.app_send_channel.aclose()
            await self.app_receive_channel.aclose()

    async def wait_for_startup(self) -> None:
        if not self.supported:
            return

        await self.app_send_channel.send({'type': 'lifespan.startup'})
        try:
            with anyio.fail_after(self.config.startup_timeout):
                await self.startup.wait()
        except TimeoutError as error:
            raise LifespanTimeoutError('startup') from error

    async def wait_for_shutdown(self) -> None:
        if not self.supported:
            return

        await self.app_send_channel.send({'type': 'lifespan.shutdown'})
        try:
            with anyio.fail_after(self.config.shutdown_timeout):
                await self.shutdown.wait()
        except TimeoutError as error:
            raise LifespanTimeoutError('startup') from error

    async def asgi_receive(self) -> AsgiReceiveEvent:
        return await self.app_receive_channel.receive()

    async def asgi_send(self, message: AsgiSendEvent) -> None:
        if message['type'] == 'lifespan.startup.complete':
            self.startup.set()

        elif message['type'] == 'lifespan.shutdown.complete':
            self.shutdown.set()

        elif message['type'] == 'lifespan.startup.failed':
            raise LifespanFailureError('startup', message.get('message', ''))

        elif message['type'] == 'lifespan.shutdown.failed':
            raise LifespanFailureError('shutdown', message.get('message', ''))

        else:
            raise UnexpectedMessageError(message['type'])
