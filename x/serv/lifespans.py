import asyncio
import functools
import logging
import typing as ta

from .config import Config
from .types import ASGIReceiveEvent
from .types import ASGISendEvent
from .types import AppWrapper
from .types import LifespanScope
from .types import UnexpectedMessageError


log = logging.getLogger(__name__)


class LifespanTimeoutError(Exception):
    def __init__(self, stage: str) -> None:
        super().__init__(
            f"Timeout whilst awaiting {stage}. Your application may not support the ASGI Lifespan "
            f"protocol correctly, alternatively the {stage}_timeout configuration is incorrect."
        )


class LifespanFailureError(Exception):
    def __init__(self, stage: str, message: str) -> None:
        super().__init__(f"Lifespan failure in {stage}. '{message}'")


class Lifespan:
    def __init__(self, app: AppWrapper, config: Config, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__()
        self.app = app
        self.config = config
        self.startup = asyncio.Event()
        self.shutdown = asyncio.Event()
        self.app_queue: asyncio.Queue = asyncio.Queue(config.max_app_queue_size)  # TODO: anyio.create_memory_object_stream  # noqa
        self.supported = True
        self.loop = loop

        # This mimics the Trio nursery.start task_status and is
        # required to ensure the support has been checked before
        # waiting on timeouts.
        self._started = asyncio.Event()

    async def handle_lifespan(self) -> None:
        self._started.set()
        scope: LifespanScope = {
            "type": "lifespan",
            "asgi": {"spec_version": "2.0", "version": "3.0"},
        }

        def _call_soon(func: ta.Callable, *args: ta.Any) -> ta.Any:
            future = asyncio.run_coroutine_threadsafe(func(*args), self.loop)
            return future.result()

        try:
            await self.app(
                scope,
                self.asgi_receive,
                self.asgi_send,
                functools.partial(self.loop.run_in_executor, None),
                _call_soon,
            )
        except LifespanFailureError:
            # Lifespan failures should crash the server
            raise
        except Exception as e:  # noqa
            self.supported = False
            if not self.startup.is_set():
                log.warning(
                    "ASGI Framework Lifespan error, continuing without Lifespan support"
                )
            elif not self.shutdown.is_set():
                log.exception(
                    "ASGI Framework Lifespan error, shutdown without Lifespan support"
                )
            else:
                log.exception("ASGI Framework Lifespan errored after shutdown.")
        finally:
            self.startup.set()
            self.shutdown.set()

    async def wait_for_startup(self) -> None:
        await self._started.wait()
        if not self.supported:
            return

        await self.app_queue.put({"type": "lifespan.startup"})
        try:
            await asyncio.wait_for(self.startup.wait(), timeout=self.config.startup_timeout)
        except asyncio.TimeoutError as error:
            raise LifespanTimeoutError("startup") from error

    async def wait_for_shutdown(self) -> None:
        await self._started.wait()
        if not self.supported:
            return

        await self.app_queue.put({"type": "lifespan.shutdown"})
        try:
            await asyncio.wait_for(self.shutdown.wait(), timeout=self.config.shutdown_timeout)
        except asyncio.TimeoutError as error:
            raise LifespanTimeoutError("shutdown") from error

    async def asgi_receive(self) -> ASGIReceiveEvent:
        return await self.app_queue.get()

    async def asgi_send(self, message: ASGISendEvent) -> None:
        if message["type"] == "lifespan.startup.complete":
            self.startup.set()
        elif message["type"] == "lifespan.shutdown.complete":
            self.shutdown.set()
        elif message["type"] == "lifespan.startup.failed":
            self.startup.set()
            raise LifespanFailureError("startup", message.get("message", ""))
        elif message["type"] == "lifespan.shutdown.failed":
            self.shutdown.set()
            raise LifespanFailureError("shutdown", message.get("message", ""))
        else:
            raise UnexpectedMessageError(message["type"])

