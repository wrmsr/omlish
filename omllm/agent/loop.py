import typing as ta

from omcore import dataclasses as dc

from .. import llm
from .events import EventSink
from .types import Context


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class LoopConfig:
    pass


class Loop:
    def __init__(
            self,
            *,
            config: LoopConfig | None = None,
            context: Context | None = None,
            sink: EventSink | None = None,
            llm_backend: llm.ImmediateBackend,
    ) -> None:
        super().__init__()

        if config is None:
            config = LoopConfig()
        self._initial_config = config
        if context is None:
            context = Context()
        self._initial_context = context
        self._sink = sink
        self._llm_backend = llm_backend

        self._config = config
        self._context = context

    async def run(self) -> None:
        pass
