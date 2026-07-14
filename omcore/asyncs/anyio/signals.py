import signal
import typing as ta

import anyio.abc


##


async def install_shutdown_signal_handler(
        tg: anyio.abc.TaskGroup,
        event: anyio.Event | None = None,
        *,
        signals: ta.Iterable[int] = (signal.SIGINT, signal.SIGTERM),
        echo: bool = False,
) -> ta.Callable[..., ta.Awaitable[None]] | None:
    if event is None:
        event = anyio.Event()

    async def _handler(*, task_status=anyio.TASK_STATUS_IGNORED):
        with anyio.open_signal_receiver(*signals) as it:  # type: ignore
            task_status.started()
            async for signum in it:
                if echo:
                    if signum == signal.SIGINT:
                        print('Ctrl+C pressed!')
                    else:
                        print('Terminated!')
                event.set()
                return

    await tg.start(_handler)
    return event.wait
