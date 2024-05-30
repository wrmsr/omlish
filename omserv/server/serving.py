import typing as ta

from .config import Config
from .types import ASGIFramework
from .types import wrap_app
from .workers import worker_serve


async def serve(
        app: ASGIFramework,
        config: Config,
        *,
        shutdown_trigger: ta.Optional[ta.Callable[..., ta.Awaitable]] = None,
        **kwargs: ta.Any
) -> None:
    await worker_serve(
        wrap_app(app),
        config,
        shutdown_trigger=shutdown_trigger,
        **kwargs
    )
