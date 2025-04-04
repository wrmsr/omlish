import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .messages import AiMessage
from .messages import Chat
from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import Service_


##


@dc.dataclass(frozen=True)
class AiChoice(lang.Final):
    m: AiMessage


AiChoices: ta.TypeAlias = ta.Sequence[AiChoice]


##


class ChatRequestOption(RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class ChatRequest(Request[ChatRequestOption]):
    chat: Chat


##


class ChatResponseOutput(ResponseOutput, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class ChatResponse(Response[ChatResponseOutput]):
    choices: AiChoices


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class ChatService(  # noqa
    Service_[
        ChatRequest,
        ChatResponse,
    ],
    lang.Abstract,
    request=ChatRequest,
    response=ChatResponse,
):
    pass
