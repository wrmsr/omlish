from ...... import minichain as mc
from ..tools.execution import ToolUseExecutor
from .types import AiChatGenerator


##


class ToolExecutingAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: AiChatGenerator,
            executor: ToolUseExecutor,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._executor = executor

    async def get_next_ai_messages(self, chat: 'mc.Chat') -> 'mc.Chat':
        out: list[mc.Message] = []

        while True:
            new = await self._wrapped.get_next_ai_messages([*chat, *out])

            cont = False

            for msg in new:
                out.append(msg)

                if isinstance(msg, mc.ToolUseMessage):
                    trm = await self._executor.execute_tool_use(msg.tu)

                    out.append(trm)

                    cont = True

            if not cont:
                return out
