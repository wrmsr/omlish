import dataclasses as dc
import typing as ta

from omlish import lang
from omlish import typedvalues as tv

from ...types import Option
from ...types import Output
from ..requests import Request
from ..responses import Response
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


class MaxTokens(Option, tv.UniqueScalarTypedValue[int]):
    pass


class Temperature(Option, tv.UniqueScalarTypedValue[float]):
    pass


ChatOption: ta.TypeAlias = MaxTokens | Temperature

ChatRequest: ta.TypeAlias = Request[Chat, ChatOption]


#


class TokenUsage(Output, tv.UniqueScalarTypedValue[int]):
    pass


class ElapsedTime(Output, tv.UniqueScalarTypedValue[float]):
    pass


ChatOutput: ta.TypeAlias = TokenUsage | ElapsedTime

ChatResponse: ta.TypeAlias = Response[Message, ChatOutput]


#


ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]


##
# local


class ModelPath(Option, tv.ScalarTypedValue[str]):
    pass


LocalChatOption: ta.TypeAlias = ChatOption | ModelPath

LocalChatRequest: ta.TypeAlias = Request[Chat, LocalChatOption]


#


class LogPath(Output, tv.ScalarTypedValue[str]):
    pass


LocalChatOutput: ta.TypeAlias = ChatOutput | LogPath

LocalChatResponse: ta.TypeAlias = Response[Message, LocalChatOutput]


#


LocalChatService: ta.TypeAlias = Service[LocalChatRequest, LocalChatResponse]


##
# remote


class ApiKey(Option, tv.ScalarTypedValue[str]):
    pass


RemoteChatOption: ta.TypeAlias = ChatOption | ApiKey

RemoteChatRequest: ta.TypeAlias = Request[Chat, RemoteChatOption]


#


class BilledCostInUsd(Output, tv.UniqueScalarTypedValue[float]):
    pass


RemoteChatOutput: ta.TypeAlias = ChatOutput | BilledCostInUsd

RemoteChatResponse: ta.TypeAlias = Response[Message, RemoteChatOutput]


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
