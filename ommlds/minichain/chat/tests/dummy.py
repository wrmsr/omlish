import dataclasses as dc
import typing as ta

from omlish import check

from ...resources import UseResources
from ...stream.services import new_stream_response
from ..choices.services import ChatChoicesRequest
from ..choices.services import ChatChoicesResponse
from ..choices.services import static_check_is_chat_choices_service
from ..choices.types import AiChoice
from ..messages import AiMessage
from ..messages import Chat
from ..messages import UserMessage
from ..services import ChatRequest
from ..services import ChatResponse
from ..services import static_check_is_chat_service
from ..stream.services import ChatChoicesStreamGenerator
from ..stream.services import ChatChoicesStreamRequest
from ..stream.services import ChatChoicesStreamResponse
from ..stream.services import static_check_is_chat_choices_stream_service
from ..stream.types import AiChoiceDelta
from ..stream.types import AiMessageDelta


##


DummyFn: ta.TypeAlias = ta.Callable[[Chat], AiMessage]
SimpleDummyFn: ta.TypeAlias = ta.Callable[[str], str]


def simple_dummy_fn(simple_fn: SimpleDummyFn) -> DummyFn:
    def inner(chat: Chat) -> AiMessage:
        return AiMessage(simple_fn(check.isinstance(check.isinstance(chat[-1], UserMessage).c, str)))
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
    def invoke(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(self.fn(request.v))


##


@static_check_is_chat_choices_service
class DummyChatChoicesService(DummyFnService):
    def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        return ChatChoicesResponse([AiChoice(self.fn(request.v))])


##


@static_check_is_chat_choices_stream_service
class DummyChatChoicesStreamService(DummyFnService):
    def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        with UseResources.or_new(request.options) as rs:
            def yield_choices() -> ChatChoicesStreamGenerator:
                am = self.fn(request.v)
                yield [AiChoiceDelta(AiMessageDelta(
                    am.s,
                    # FIXME
                    # am.tool_exec_requests,
                    None,
                ))]
                return []
            return new_stream_response(rs, yield_choices())
