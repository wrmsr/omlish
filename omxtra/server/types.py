import typing as ta


##


AsgiReceiveEvent: ta.TypeAlias = ta.Mapping[str, ta.Any]
AsgiSendEvent: ta.TypeAlias = ta.Mapping[str, ta.Any]

AsgiReceiveCallable: ta.TypeAlias = ta.Callable[[], ta.Awaitable[AsgiReceiveEvent]]
AsgiSendCallable: ta.TypeAlias = ta.Callable[[AsgiSendEvent], ta.Awaitable[None]]

Scope: ta.TypeAlias = ta.Mapping[str, ta.Any]
AsgiFramework: ta.TypeAlias = ta.Callable[
    [
        Scope,
        AsgiReceiveCallable,
        AsgiSendCallable,
    ],
    ta.Awaitable[None],
]

LifespanScope: ta.TypeAlias = Scope

HttpResponseStartEvent: ta.TypeAlias = ta.Mapping[str, ta.Any]
HttpScope: ta.TypeAlias = Scope
WebsocketScope: ta.TypeAlias = Scope

WebsocketAcceptEvent: ta.TypeAlias = ta.Mapping[str, ta.Any]
WebsocketResponseBodyEvent: ta.TypeAlias = ta.Mapping[str, ta.Any]
WebsocketResponseStartEvent: ta.TypeAlias = ta.Mapping[str, ta.Any]


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
        app: AsgiFramework | AppWrapper,
) -> AppWrapper:
    if isinstance(app, AsgiWrapper):
        return app
    return AsgiWrapper(app)  # type: ignore


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
