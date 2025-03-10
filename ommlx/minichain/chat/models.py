import abc
import collections.abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..generative import Generative
from ..models import Model
from ..models import ModelRequest
from ..models import ModelResponse
from .messages import AiMessage
from .messages import Chat
from .messages import Message
from .options import ChatOptions


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
@dc.extra_params(generic_init=True)
class ChatRequest(
    ModelRequest[
        ChatInput,
        ChatOptions,
        ChatNew,
    ],
    lang.Final,
):
    @classmethod
    def new(
            cls,
            v: ChatNew,
            *options: ChatOptions,
            **kwargs: ta.Any,
    ) -> 'ChatRequest':
        if isinstance(v, Message):
            v = (v,)

        return super().new(
            v,
            *options,
            **kwargs,
        )

    @dc.validate
    def _validate_v(self) -> bool:
        return (
            not isinstance(self.v, str) and  # type: ignore[unreachable]
            isinstance(self.v, collections.abc.Sequence) and
            all(isinstance(e, Message) for e in self.v)
        )


@dc.dataclass(frozen=True, kw_only=True)
class ChatResponse(ModelResponse[ChatOutput], lang.Final):
    pass


class ChatModel(
    Model[
        ChatRequest,
        ChatOptions,
        ChatNew,
        ChatResponse,
    ],
    Generative,
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError
