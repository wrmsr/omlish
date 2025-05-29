import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..llms.services import LlmRequestOption
from ..llms.services import LlmResponseOutput
from ..services import Request
from ..services import Service_
from ..streaming import StreamResponse
from .choices import AiChoices
from .messages import Chat
from .types import ChatRequestOption
from .types import ChatResponseOutput


ChatStreamRequestOptionT = ta.TypeVar('ChatStreamRequestOptionT', bound=ChatRequestOption | LlmRequestOption)
ChatStreamRequestT = ta.TypeVar('ChatStreamRequestT', bound='ChatStreamRequest')
ChatStreamResponseOutputT = ta.TypeVar('ChatStreamResponseOutputT', bound=ChatResponseOutput | LlmResponseOutput)
ChatStreamResponseT = ta.TypeVar('ChatStreamResponseT', bound='ChatStreamResponse')


##


@dc.dataclass(frozen=True)
class ChatStreamRequest(Request[ChatStreamRequestOptionT]):
    chat: Chat


##


@dc.dataclass(frozen=True)
class ChatStreamResponse(StreamResponse[ChatStreamResponseOutputT, AiChoices]):
    _iterator: ta.Iterator[AiChoices]

    def __iter__(self) -> ta.Iterator[AiChoices]:
        return self._iterator


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendTypeManifest
class ChatStreamService(  # noqa
    Service_[
        ChatStreamRequestT,
        ChatStreamResponseT,
    ],
    lang.Abstract,
    ta.Generic[
        ChatStreamRequestT,
        ChatStreamResponseT,
    ],
    request=ChatStreamRequest,
    response=ChatStreamResponse,
):
    pass


ChatStreamService_: ta.TypeAlias = ChatStreamService[ChatStreamRequest, ChatStreamResponse]
