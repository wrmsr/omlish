import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..llms.services import LlmRequestOption
from ..llms.services import LlmResponseOutput
from ..services import Request
from ..services import Response
from ..services import Service_
from .choices import AiChoices
from .messages import Chat
from .types import ChatRequestOption
from .types import ChatResponseOutput


ChatRequestOptionT = ta.TypeVar('ChatRequestOptionT', bound=ChatRequestOption | LlmRequestOption)
ChatRequestT = ta.TypeVar('ChatRequestT', bound='ChatRequest')
ChatResponseOutputT = ta.TypeVar('ChatResponseOutputT', bound=ChatResponseOutput | LlmResponseOutput)
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


# @omlish-manifest ommlds.minichain.backends.manifests.BackendTypeManifest
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
