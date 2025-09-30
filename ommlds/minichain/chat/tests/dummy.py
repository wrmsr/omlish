import dataclasses as dc
import typing as ta

from omlish import check

from ...resources import UseResources
from ...stream.services import StreamResponseSink
from ...stream.services import new_stream_response
from ..choices.services import ChatChoicesOutputs
from ..choices.services import ChatChoicesRequest
from ..choices.services import ChatChoicesResponse
from ..choices.services import static_check_is_chat_choices_service
from ..choices.types import AiChoice
from ..messages import AiChat
from ..messages import AiMessage
from ..messages import Chat
from ..messages import UserMessage
from ..services import ChatRequest
from ..services import ChatResponse
from ..services import static_check_is_chat_service
from ..stream.services import ChatChoicesStreamRequest
from ..stream.services import ChatChoicesStreamResponse
from ..stream.services import static_check_is_chat_choices_stream_service
from ..stream.types import AiChoiceDeltas
from ..stream.types import AiChoicesDeltas
from ..stream.types import ContentAiChoiceDelta


##


DummyFn: ta.TypeAlias = ta.Callable[[Chat], AiChat]
SimpleDummyFn: ta.TypeAlias = ta.Callable[[str], str]


def simple_dummy_fn(simple_fn: SimpleDummyFn) -> DummyFn:
    def inner(chat: Chat) -> AiChat:
        return [AiMessage(simple_fn(check.isinstance(check.isinstance(chat[-1], UserMessage).c, str)))]
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
        return ChatChoicesResponse([AiChoice(self.fn(request.v))])


##


@static_check_is_chat_choices_stream_service
class DummyChatChoicesStreamService(DummyFnService):
    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        async with UseResources.or_new(request.options) as rs:
            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs]:
                ac = self.fn(request.v)
                await sink.emit(AiChoicesDeltas([
                    AiChoiceDeltas([
                        ContentAiChoiceDelta(
                            check.isinstance(am, AiMessage).c,
                        )
                        for am in ac
                    ]),
                ]))
                return []
            return await new_stream_response(rs, inner)
