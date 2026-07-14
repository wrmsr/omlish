import abc
import typing as ta

from omlish import lang

from ...registries.globals import register_type
from ...services import Request
from ...services import Service
from ...services import StreamResponse
from ...types import Output
from ..messages import Chat
from .types import AiDeltas
from .types import ChatStreamOptions
from .types import ChatStreamResult


##


class ChatStreamServiceOutput(Output, lang.Abstract, lang.Sealed):
    pass


ChatStreamServiceOutputs: ta.TypeAlias = ChatStreamServiceOutput


##


ChatStreamRequest: ta.TypeAlias = Request[Chat, ChatStreamOptions]

ChatStreamResponse: ta.TypeAlias = StreamResponse[
    AiDeltas,
    ChatStreamResult,
    ChatStreamServiceOutputs,
]

# @om-manifest $.minichain.registries.manifests.RegistryTypeManifest
ChatStreamService: ta.TypeAlias = Service[ChatStreamRequest, ChatStreamResponse]

register_type(ChatStreamService, module=__name__)


def static_check_is_chat_stream_service[T: ChatStreamService](t: type[T]) -> type[T]:
    return t


##


@static_check_is_chat_stream_service
class AbstractChatStreamService(lang.Abstract):
    @abc.abstractmethod
    def invoke(self, request: ChatStreamRequest) -> ta.Awaitable[ChatStreamResponse]:
        raise NotImplementedError
