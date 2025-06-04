import dataclasses as dc
import typing as ta

from omlish import lang
from omlish import typedvalues as tv

from ..requests import Request
from ..requests import RequestOption
from ..responses import Response
from ..responses import ResponseOutput
from ..services import Service


##
# types


@dc.dataclass(frozen=True)
class Message:
    role: str
    message: str


Chat: ta.TypeAlias = ta.Sequence[Message]


##
# base


class MaxTokens(RequestOption, tv.UniqueScalarTypedValue[int]):
    pass


class Temperature(RequestOption, tv.UniqueScalarTypedValue[float]):
    pass


ChatRequestOption: ta.TypeAlias = MaxTokens | Temperature

ChatRequest: ta.TypeAlias = Request[Chat, ChatRequestOption]


#


class TokenUsage(ResponseOutput, tv.UniqueScalarTypedValue[int]):
    pass


class ElapsedTime(ResponseOutput, tv.UniqueScalarTypedValue[float]):
    pass


ChatResponseOutput: ta.TypeAlias = TokenUsage | ElapsedTime

ChatResponse: ta.TypeAlias = Response[Message, ChatResponseOutput]


#


ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]


##
# local


class ModelPath(RequestOption, tv.ScalarTypedValue[str]):
    pass


LocalChatRequestOption: ta.TypeAlias = ChatRequestOption | ModelPath

LocalChatRequest: ta.TypeAlias = Request[Chat, LocalChatRequestOption]


#


class LogPath(ResponseOutput, tv.ScalarTypedValue[str]):
    pass


LocalChatResponseOutput: ta.TypeAlias = ChatResponseOutput | LogPath

LocalChatResponse: ta.TypeAlias = Response[Message, LocalChatResponseOutput]


#


LocalChatService: ta.TypeAlias = Service[LocalChatRequest, LocalChatResponse]


##
# remote


class ApiKey(RequestOption, tv.ScalarTypedValue[str]):
    pass


RemoteChatRequestOption: ta.TypeAlias = ChatRequestOption | ApiKey

RemoteChatRequest: ta.TypeAlias = Request[Chat, RemoteChatRequestOption]


#


class BilledCostInUsd(ResponseOutput, tv.UniqueScalarTypedValue[float]):
    pass


RemoteChatResponseOutput: ta.TypeAlias = ChatResponseOutput | BilledCostInUsd

RemoteChatResponse: ta.TypeAlias = Response[Message, RemoteChatResponseOutput]


#


RemoteChatService: ta.TypeAlias = Service[RemoteChatRequest, RemoteChatResponse]


##
# impls


class RemoteChatServiceImpl:  # (RemoteChatService):
    def invoke(self, request: RemoteChatRequest) -> RemoteChatResponse:
        return RemoteChatResponse(
            Message('ai', f'(remote reply): {request.v[-1].message}'),
            [
                TokenUsage(2),
                BilledCostInUsd(0.05),
            ],
        )


lang.static_check_issubclass[RemoteChatService](RemoteChatServiceImpl)
lang.static_check_issubclass[ChatService](RemoteChatServiceImpl)

# Negative test - mypy will report unused ignores via warn_unused_ignores
lang.static_check_issubclass[LocalChatService](RemoteChatServiceImpl)  # type: ignore[arg-type]


#


class LocalChatServiceImpl:  # (LocalChatService):
    def invoke(self, request: LocalChatRequest) -> LocalChatResponse:
        return LocalChatResponse(
            Message('ai', f'(local reply): {request.v[-1].message}'),
            [
                TokenUsage(1),
                LogPath('log.txt'),
            ],
        )


lang.static_check_issubclass[LocalChatService](LocalChatServiceImpl)
lang.static_check_issubclass[ChatService](LocalChatServiceImpl)

# Negative test - mypy will report unused ignores via warn_unused_ignores
lang.static_check_issubclass[RemoteChatService](LocalChatServiceImpl)  # type: ignore[arg-type]
