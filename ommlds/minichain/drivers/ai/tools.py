from ...chat.messages import Chat
from ...chat.messages import Message
from ...chat.messages import ToolUseMessage
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

    async def get_next_ai_messages(self, chat: Chat) -> Chat:
        out: list[Message] = []

        while True:
            new = await self._wrapped.get_next_ai_messages([*chat, *out])

            cont = False

            for msg in new:
                out.append(msg)

                if isinstance(msg, ToolUseMessage):
                    trm = await self._executor.execute_tool_use(msg.tu)

                    out.append(trm)

                    cont = True

            if not cont:
                return out
