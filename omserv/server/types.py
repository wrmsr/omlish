import typing as ta


##


AsgiReceiveEvent: ta.TypeAlias = dict
AsgiSendEvent: ta.TypeAlias = dict

AsgiReceiveCallable: ta.TypeAlias = ta.Callable[[], ta.Awaitable[AsgiReceiveEvent]]
AsgiSendCallable: ta.TypeAlias = ta.Callable[[AsgiSendEvent], ta.Awaitable[None]]

Scope: ta.TypeAlias = dict
AsgiFramework: ta.TypeAlias = ta.Callable[
    [
        Scope,
        AsgiReceiveCallable,
        AsgiSendCallable,
    ],
    ta.Awaitable[None],
]

LifespanScope: ta.TypeAlias = Scope

HTTPResponseStartEvent: ta.TypeAlias = dict
HTTPScope: ta.TypeAlias = Scope
WebsocketScope: ta.TypeAlias = Scope

WebsocketAcceptEvent: ta.TypeAlias = dict
WebsocketResponseBodyEvent: ta.TypeAlias = dict
WebsocketResponseStartEvent: ta.TypeAlias = dict


##


class UnexpectedMessageError(Exception):
    pass


class AsgiWrapper:
    def __init__(self, app: AsgiFramework) -> None:
        super().__init__()
        self.app = app

    async def __call__(
            self,
            scope: Scope,
            receive: AsgiReceiveCallable,
            send: AsgiSendCallable,
            sync_spawn: ta.Callable,
            call_soon: ta.Callable,
    ) -> None:
        await self.app(scope, receive, send)


class AppWrapper(ta.Protocol):
    async def __call__(
            self,
            scope: Scope,
            receive: AsgiReceiveCallable,
            send: AsgiSendCallable,
            sync_spawn: ta.Callable,
            call_soon: ta.Callable,
    ) -> None:
        pass


def wrap_app(
        app: AsgiFramework,
) -> AppWrapper:
    return AsgiWrapper(app)


##


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
