import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from .. import llm
from .contexts import Context
from .events import AgentEndEvent
from .events import AgentStartEvent
from .events import Event
from .events import EventSink
from .events import TurnEndEvent
from .events import TurnStartEvent
from .messages import Message
from .tools import ToolContext


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class LoopConfig:
    llm_options: llm.Options | None = None


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class LoopResult:
    config: LoopConfig
    context: Context

    new_messages: ta.Sequence[Message] | None = None


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

        #

        self._config = config
        self._context = context

        self._new_messages: list[Message] = []

    #

    async def _emit(self, event: Event) -> None:
        if (sink := self._sink) is not None:
            await sink(event)

    #

    async def _llm_complete(self) -> llm.AiMessage:
        llm_context = llm.Context(
            system_prompt=self._context.system_prompt,

            messages=[  # noqa
                m
                for m in self._context.messages
            ] if self._context.messages is not None else None,

            tools=[
                t.llm_tool
                for t in self._context.tools
            ] if self._context.tools else None,
        )

        return await self._llm_backend.immediate(
            llm_context,
            self._config.llm_options,
        )

    #

    @dc.dataclass(frozen=True, kw_only=True)
    class _TurnResult:
        should_continue: bool

    async def _turn(self) -> _TurnResult:
        await self._emit(TurnStartEvent())

        message = await self._llm_complete()  # noqa

        self._new_messages.append(message)

        if message.stop_reason is not None:
            await self._emit(TurnEndEvent(
                message=message,
            ))

            return self._TurnResult(
                should_continue=False,
            )

        tool_calls = [c for c in message.content if isinstance(c, llm.ToolCall)]
        if tool_calls:
            for tool_call in tool_calls:
                tool = self._context.tools_by_name[tool_call.name]

                tool_result = await tool.executor(ToolContext(  # noqa
                    llm_tool_call=tool_call,
                ))

                raise NotImplementedError

        await self._emit(TurnEndEvent(
            message=message,
        ))

        return self._TurnResult(
            should_continue=bool(tool_calls),
        )

    #

    async def run(self) -> LoopResult:
        await self._emit(AgentStartEvent())

        while True:
            turn_result = await self._turn()

            if not turn_result.should_continue:
                break

        await self._emit(AgentEndEvent(
            context=self._context,

            new_messages=self._new_messages,
        ))

        return LoopResult(
            config=self._config,
            context=self._context,

            new_messages=self._new_messages,
        )
