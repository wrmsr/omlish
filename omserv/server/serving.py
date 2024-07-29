import typing as ta

from .config import Config
from .types import AsgiFramework
from .types import wrap_app
from .workers import worker_serve


async def serve(
        app: AsgiFramework,
        config: Config,
        **kwargs: ta.Any,
) -> None:
    await worker_serve(
        wrap_app(app),
        config,
        **kwargs,
    )
