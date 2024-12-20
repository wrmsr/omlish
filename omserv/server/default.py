import typing as ta

import anyio.abc

from omlish import inject as inj

from .config import Config
from .inject import bind_server
from .listener import Listener
from .sockets import Sockets
from .types import AppWrapper
from .types import AsgiFramework
from .types import wrap_app


async def serve(
        app: AsgiFramework | AppWrapper,
        config: Config,
        *,
        sockets: Sockets | None = None,
        shutdown_trigger: ta.Callable[..., ta.Awaitable[None]] | None = None,
        handle_shutdown_signals: bool = False,
        task_status: anyio.abc.TaskStatus[ta.Sequence[str]] = anyio.TASK_STATUS_IGNORED,
) -> None:
    injector = inj.create_injector(bind_server(config))
    listener = injector.inject(Listener)
    await listener.listen(
        wrap_app(app),
        config,
        sockets=sockets,
        shutdown_trigger=shutdown_trigger,
        handle_shutdown_signals=handle_shutdown_signals,
        task_status=task_status,
    )
