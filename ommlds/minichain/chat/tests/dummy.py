import dataclasses as dc
import typing as ta

from omlish import check

from ...resources import UseResources
from ...services import StreamResponseSink
from ...services import new_stream_response
from ..choices.services import ChatChoicesRequest
from ..choices.services import ChatChoicesResponse
from ..choices.services import static_check_is_chat_choices_service
from ..choices.types import ChatChoices
from ..generations import ChatGeneration
from ..messages import AiMessage
from ..messages import Chat
from ..messages import UserMessage
from ..services import ChatRequest
from ..services import ChatResponse
from ..services import static_check_is_chat_service
from ..stream.choices.services import ChatChoicesStreamRequest
from ..stream.choices.services import ChatChoicesStreamResponse
from ..stream.choices.services import static_check_is_chat_choices_stream_service
from ..stream.choices.types import AiChoiceDeltas
from ..stream.choices.types import AiChoicesDeltas
from ..stream.choices.types import ChatChoicesStreamResult
from ..stream.types import ContentAiDelta


##


DummyFn: ta.TypeAlias = ta.Callable[[Chat], ChatGeneration]
SimpleDummyFn: ta.TypeAlias = ta.Callable[[str], str]


def simple_dummy_fn(simple_fn: SimpleDummyFn) -> DummyFn:
    def inner(chat: Chat) -> ChatGeneration:
        return ChatGeneration([
            AiMessage(
                simple_fn(
                    check.isinstance(check.isinstance(chat[-1], UserMessage).c, str),
                ),
            ),
        ])
    return inner


@dc.dataclass(frozen=True)
class DummyFnService:
    fn: DummyFn

    @classmethod
    def simple(cls, simple_fn: SimpleDummyFn) -> ta.Self:
        return cls(simple_dummy_fn(simple_fn))


##


@static_check_is_chat_service
class DummyChatService(DummyFnService):
    async def invoke(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(self.fn(request.v))


##


@static_check_is_chat_choices_service
class DummyChatChoicesService(DummyFnService):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        return ChatChoicesResponse(ChatChoices([self.fn(request.v)]))


##


@static_check_is_chat_choices_stream_service
class DummyChatChoicesStreamService(DummyFnService):
    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ChatChoicesStreamResult:
                acg = self.fn(request.v)
                await sink.emit(AiChoicesDeltas([
                    AiChoiceDeltas([
                        ContentAiDelta(
                            check.isinstance(am, AiMessage).c,
                        )
                        for am in acg.chat
                    ]),
                ]))
                return ChatChoicesStreamResult()
            return await new_stream_response(rs, inner)
