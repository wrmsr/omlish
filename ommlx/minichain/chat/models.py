import abc
import collections.abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..generative import Generative
from ..models import Model
from ..models import Request
from ..models import Response
from .messages import AiMessage
from .messages import Chat
from .messages import Message
from .options import ChatRequestOptions


##


@dc.dataclass(frozen=True)
class AiChoice(lang.Final):
    m: AiMessage


AiChoices: ta.TypeAlias = ta.Sequence[AiChoice]


##


ChatInput: ta.TypeAlias = Chat
ChatNew: ta.TypeAlias = ta.Any
ChatOutput: ta.TypeAlias = AiChoices


@dc.dataclass(frozen=True, kw_only=True)
class ChatRequest(
    Request[
        ChatInput,
        ChatRequestOptions,
        ChatNew,
    ],
    lang.Final,
):
    @dc.validate
    def _validate_v(self) -> bool:
        return (
            not isinstance(self.v, str) and  # type: ignore[unreachable]
            isinstance(self.v, collections.abc.Sequence) and
            all(isinstance(e, Message) for e in self.v)
        )


@dc.dataclass(frozen=True, kw_only=True)
class ChatResponse(Response[ChatOutput], lang.Final):
    pass


class ChatModel(
    Model[
        ChatRequest,
        ChatRequestOptions,
        ChatNew,
        ChatResponse,
    ],
    Generative,
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError
