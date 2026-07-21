import typing as ta

from omcore import dataclasses as dc

from .. import llm
from .events import EventSink
from .types import Context


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class LoopConfig:
    llm_options: llm.Options | None = None


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

    #

    async def _llm_complete(self) -> llm.AiMessage:
        llm_context = llm.Context(
            system_prompt=self._context.system_prompt,

            messages=[  # noqa
                m
                for m in self._context.messages
            ] if self._context.messages is not None else None,
        )

        return await self._llm_backend.immediate(
            llm_context,
            self._config.llm_options,
        )

    #

    async def _step(self) -> None:
        out = await self._llm_complete()  # noqa

        raise NotImplementedError

    #

    async def run(self) -> None:
        while True:
            await self._step()
