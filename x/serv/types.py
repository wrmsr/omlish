import asyncio
import typing as ta


##


ASGIReceiveEvent: ta.TypeAlias = dict
ASGISendEvent: ta.TypeAlias = dict

ASGIReceiveCallable: ta.TypeAlias = ta.Callable[[], ta.Awaitable[ASGIReceiveEvent]]
ASGISendCallable: ta.TypeAlias = ta.Callable[[ASGISendEvent], ta.Awaitable[None]]

Scope: ta.TypeAlias = dict
ASGIFramework: ta.TypeAlias = ta.Callable[
    [
        Scope,
        ASGIReceiveCallable,
        ASGISendCallable,
    ],
    ta.Awaitable[None],
]

LifespanScope: ta.TypeAlias = Scope

HTTPResponseStartEvent: ta.TypeAlias = dict
HTTPScope: ta.TypeAlias = Scope


##


class UnexpectedMessageError(Exception):
    pass


class ASGIWrapper:
    def __init__(self, app: ASGIFramework) -> None:
        super().__init__()
        self.app = app

    async def __call__(
            self,
            scope: Scope,
            receive: ASGIReceiveCallable,
            send: ASGISendCallable,
            sync_spawn: ta.Callable,
            call_soon: ta.Callable,
    ) -> None:
        await self.app(scope, receive, send)


class AppWrapper(ta.Protocol):
    async def __call__(
            self,
            scope: Scope,
            receive: ASGIReceiveCallable,
            send: ASGISendCallable,
            sync_spawn: ta.Callable,
            call_soon: ta.Callable,
    ) -> None:
        pass


def wrap_app(
        app: ASGIFramework,
) -> AppWrapper:
    return ASGIWrapper(ta.cast(ASGIFramework, app))


##


# FIXME: rename to WaitableEvent
class WaitableEvent(ta.Protocol):
    def __init__(self) -> None:
        pass

    async def clear(self) -> None:
        pass

    async def set(self) -> None:
        pass

    async def wait(self) -> None:
        pass

    def is_set(self) -> bool:
        pass


class WaitableEventWrapper:
    def __init__(self) -> None:
        super().__init__()
        self._event = asyncio.Event()

    async def clear(self) -> None:
        self._event.clear()

    async def wait(self) -> None:
        await self._event.wait()

    async def set(self) -> None:
        self._event.set()

    def is_set(self) -> bool:
        return self._event.is_set()
