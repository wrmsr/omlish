import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..services import Request
from ..services import Response
from ..services import Service_
from .choices import AiChoices
from .messages import Chat
from .types import ChatRequestOption
from .types import ChatResponseOutput


ChatRequestOptionT = ta.TypeVar('ChatRequestOptionT', bound=ChatRequestOption)
ChatResponseOutputT = ta.TypeVar('ChatResponseOutputT', bound=ChatResponseOutput)


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
        ChatRequest,
        ChatResponse,
    ],
    lang.Abstract,
    request=ChatRequest,
    response=ChatResponse,
):
    pass
