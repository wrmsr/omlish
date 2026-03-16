import typing as ta
import uuid

from omlish import check

from ...chat.messages import Chat
from ...chat.metadata import MessageUuid
from ...chat.stream.types import AiDelta
from .types import AiChatGenerator
from .types import GenerateAiChatArgs
from .types import StreamAiChatGenerator


##


class UuidAddingAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: AiChatGenerator,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped

    async def generate_ai_chat(self, args: GenerateAiChatArgs) -> Chat:
        if (mu := args.message_uuid) is None:
            mu = uuid.uuid4()

        out = await self._wrapped.generate_ai_chat(args)

        msg = check.single(out)
        check.not_in(MessageUuid, msg.metadata)
        msg = msg.with_metadata(MessageUuid(mu))
        out = [msg]

        return out


class UuidAddingStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            *,
            wrapped: StreamAiChatGenerator,
    ) -> None:
        super().__init__()

        self._wrapped = wrapped

    async def generate_ai_chat_streamed(
            self,
            args: GenerateAiChatArgs,
            delta_callback: ta.Callable[[AiDelta], ta.Awaitable[None]] | None = None,
    ) -> Chat:
        if (mu := args.message_uuid) is None:
            mu = uuid.uuid4()

        async def inner(delta: AiDelta) -> None:
            check.not_in(MessageUuid, delta.metadata)
            delta = delta.with_metadata(MessageUuid(mu))

            if delta_callback is not None:
                await delta_callback(delta)

        out = await self._wrapped.generate_ai_chat_streamed(args, delta_callback=inner)

        msg = check.single(out)
        check.not_in(MessageUuid, msg.metadata)
        msg = msg.with_metadata(MessageUuid(mu))
        out = [msg]

        return out
