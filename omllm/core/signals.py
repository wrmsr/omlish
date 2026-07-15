import typing as ta


##


class AbortSignal:
    def __init__(self) -> None:
        super().__init__()

        self._aborted = False
        self._listeners: list[ta.Callable[[], ta.Awaitable[None] | None]] = []

    @property
    def aborted(self) -> bool:
        return self._aborted

    def add_listener(self, fn: ta.Callable[[], ta.Awaitable[None] | None]) -> None:
        if self._aborted:
            fn()
        else:
            self._listeners.append(fn)

    def remove_listener(self, fn: ta.Callable[[], ta.Awaitable[None] | None]) -> None:
        try:
            self._listeners.remove(fn)
        except ValueError:
            pass

    def raise_if_aborted(self) -> None:
        if self._aborted:
            raise AbortedError

    async def _abort(self) -> None:
        if self._aborted:
            return
        self._aborted = True
        listeners, self._listeners = self._listeners, []
        for fn in listeners:
            obj = fn()
            if isinstance(obj, ta.Awaitable):
                await obj


class AbortController:
    def __init__(self) -> None:
        super().__init__()

        self._signal = AbortSignal()

    @property
    def signal(self) -> AbortSignal:
        return self._signal

    async def abort(self) -> None:
        await self._signal._abort()  # noqa: SLF001


class AbortedError(Exception):
    def __init__(self, msg: str = 'Operation aborted') -> None:
        super().__init__(msg)
