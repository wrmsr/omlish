from ...... import minichain as mc
from ...tools.execution import ToolUseExecutor
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

    async def get_next_ai_messages(self, chat: 'mc.Chat') -> 'mc.AiChat':
        out = await self._wrapped.get_next_ai_messages(chat)

        for msg in out:  # noqa
            # if (c := self._extractor.extract_message_content(msg)) is not None:
            #     await self._renderer.render_content(c)
            raise NotImplementedError

        return out
