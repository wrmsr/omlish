from omlish import check
from omlish import dataclasses as dc

from ...chat.messages import Chat
from ...chat.messages import Message
from ...chat.messages import ToolUseMessage
from ...chat.messages import ToolUseResultMessage
from ...chat.transform.metadata import CreatedAtAddingMessageTransform
from ...chat.transform.metadata import MessageUuidAddingMessageTransform
from ...chat.transform.types import CompositeMessageTransform
from ...tools.execution.catalog import ToolCatalog
from ...tools.execution.execution import ToolUseExecution
from ...tools.execution.execution import ToolUseExecutor
from .types import AiChatGenerator
from .types import GenerateAiChatArgs


##


class ToolExecutingAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: AiChatGenerator,
            catalog: ToolCatalog,
            executor: ToolUseExecutor,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped
        self._catalog = catalog
        self._executor = executor

        self._mt = CompositeMessageTransform([
            CreatedAtAddingMessageTransform(),
            MessageUuidAddingMessageTransform(),
        ])

    async def generate_ai_chat(self, args: GenerateAiChatArgs) -> Chat:
        out: list[Message] = []

        while True:
            new = await self._wrapped.generate_ai_chat(
                dc.replace(args, chat=[*args.chat, *out]),
            )

            out.extend(new)

            tool_use_messages = [
                msg
                for msg in new
                if isinstance(msg, ToolUseMessage)
            ]

            for msg in tool_use_messages:
                use = msg.tu

                tce = self._catalog.by_name[check.non_empty_str(use.name)]

                trr = await self._executor.execute_tool_use(ToolUseExecution(
                    msg.tu,
                    tce,
                ))

                trm = ToolUseResultMessage(trr)

                trm = check.isinstance(check.single(self._mt.transform(trm)), ToolUseResultMessage)

                out.append(trm)

            if not tool_use_messages:
                return out
