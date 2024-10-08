import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..generative import Generative
from ..models import Model
from ..models import Request
from ..models import Response
from .messages import AiMessage
from .messages import Chat
from .options import ChatRequestOptions


##


ChatInput: ta.TypeAlias = Chat
ChatOutput: ta.TypeAlias = AiMessage


@dc.dataclass(frozen=True, kw_only=True)
class ChatRequest(Request[ChatInput, ChatRequestOptions], lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class ChatResponse(Response[ChatOutput], lang.Final):
    pass


class ChatModel(Model[ChatRequest, ChatRequestOptions, ChatResponse], Generative, lang.Abstract):
    @abc.abstractmethod
    def invoke(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError
