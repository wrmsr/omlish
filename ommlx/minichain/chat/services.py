import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import Service_
from .choices import AiChoices
from .messages import Chat


ChatRequestOptionT = ta.TypeVar('ChatRequestOptionT', bound=RequestOption)
ChatRequestT = ta.TypeVar('ChatRequestT', bound='ChatRequest')
ChatResponseOutputT = ta.TypeVar('ChatResponseOutputT', bound=ResponseOutput)
ChatResponseT = ta.TypeVar('ChatResponseT', bound='ChatResponse')


##


@dc.dataclass(frozen=True)
class ChatRequest(Request[ChatRequestOptionT]):
    chat: Chat


##


@dc.dataclass(frozen=True)
class ChatResponse(Response[ChatResponseOutputT]):
    choices: AiChoices


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class ChatService(  # noqa
    Service_[
        ChatRequestT,
        ChatResponseT,
    ],
    lang.Abstract,
    ta.Generic[
        ChatRequestT,
        ChatResponseT,
    ],
    request=ChatRequest,
    response=ChatResponse,
):
    pass


ChatService_: ta.TypeAlias = ChatService[ChatRequest, ChatResponse]
