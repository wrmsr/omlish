from omlish import dataclasses as dc

from ...chat.messages import Chat
from ...chat.messages import Message
from ...chat.messages import ToolUseMessage
from ..tools.execution import ToolUseExecutor
from .types import AiChatGenerator
from .types import GenerateAiChatArgs


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

    async def generate_ai_chat(self, args: GenerateAiChatArgs) -> Chat:
        out: list[Message] = []

        while True:
            new = await self._wrapped.generate_ai_chat(
                dc.replace(args, chat=[*args.chat, *out]),
            )

            cont = False

            for msg in new:
                out.append(msg)

                if isinstance(msg, ToolUseMessage):
                    trm = await self._executor.execute_tool_use(msg.tu)

                    out.append(trm)

                    cont = True

            if not cont:
                return out
