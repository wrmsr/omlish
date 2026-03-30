import typing as ta

from omlish import check
from omlish import lang

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesService
from ...chat.choices.stream.services import ChatChoicesStreamRequest
from ...chat.choices.stream.services import ChatChoicesStreamService
from ...chat.choices.types import ChatChoicesOptions
from ...chat.messages import AiChat
from ...chat.messages import Chat
from ...chat.stream.joining import AiDeltaJoiner
from ...chat.stream.transform.types import AiDeltaTransformAiDeltasTransform
from ...chat.stream.transform.uuids import TypeSequentialMessageUuidAddingAiDeltaTransform
from ...chat.stream.types import AiDelta
from ...chat.transform.metadata import MessageUuidAddingMessageTransform
from ...chat.transform.types import CompositeMessageTransform
from ...chat.transform.types import MessageTransformChatTransform
from .types import AiChatGenerator
from .types import GenerateAiChatArgs
from .types import StreamAiChatGenerator


##


class ChatChoicesServiceOptionsProvider(lang.Func0[ta.Sequence[ChatChoicesOptions]]):
    pass


ChatChoicesServiceOptionsProviders = ta.NewType('ChatChoicesServiceOptionsProviders', ta.Sequence[ChatChoicesServiceOptionsProvider])  # noqa


##


class ChatChoicesServiceAiChatGenerator(AiChatGenerator):
    def __init__(
            self,
            service: ChatChoicesService,
            *,
            options: ChatChoicesServiceOptionsProvider | None = None,
    ) -> None:
        super().__init__()

        self._service = service
        self._options = options

        self._mt = MessageTransformChatTransform(
            CompositeMessageTransform([
                MessageUuidAddingMessageTransform(),
            ]),
        )

    async def generate_ai_chat(self, args: GenerateAiChatArgs) -> Chat:
        opts = self._options() if self._options is not None else []

        resp = await self._service.invoke(ChatChoicesRequest(args.chat, opts))

        out: Chat = check.single(resp.v).chat

        out = self._mt.transform(out)

        return out


class ChatChoicesStreamServiceStreamAiChatGenerator(StreamAiChatGenerator):
    def __init__(
            self,
            service: ChatChoicesStreamService,
            *,
            options: ChatChoicesServiceOptionsProvider | None = None,
    ) -> None:
        super().__init__()

        self._service = service
        self._options = options

    async def generate_ai_chat_streamed(
            self,
            args: GenerateAiChatArgs,
            delta_callback: ta.Callable[[AiDelta], ta.Awaitable[None]] | None = None,
    ) -> AiChat:
        opts = self._options() if self._options is not None else []

        joiner = AiDeltaJoiner()

        dt = AiDeltaTransformAiDeltasTransform(
            TypeSequentialMessageUuidAddingAiDeltaTransform(),
        )

        async with (await self._service.invoke(ChatChoicesStreamRequest(args.chat, opts))).v as st_resp:
            async for o in st_resp:
                ds = check.single(o.choices).deltas

                ds = dt.transform(ds)

                joiner.add(ds)

                for delta in ds:
                    if delta_callback is not None:
                        await delta_callback(delta)

        out = joiner.build()

        return out
