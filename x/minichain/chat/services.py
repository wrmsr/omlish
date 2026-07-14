import abc
import typing as ta

from omlish import lang

from ..registries.globals import register_type
from ..services import Request
from ..services import Response
from ..services import Service
from ..types import Output
from .generations import ChatGeneration
from .messages import Chat
from .types import ChatOptions


##


class ChatServiceOutput(Output, lang.Abstract, lang.Sealed):
    pass


ChatServiceOutputs: ta.TypeAlias = ChatServiceOutput


##


ChatRequest: ta.TypeAlias = Request[Chat, ChatOptions]

ChatResponse: ta.TypeAlias = Response[ChatGeneration, ChatServiceOutputs]

# @om-manifest $.minichain.registries.manifests.RegistryTypeManifest
ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]

register_type(ChatService, module=__name__)


def static_check_is_chat_service[T: ChatService](t: type[T]) -> type[T]:
    return t


##


@static_check_is_chat_service
class AbstractChatService(lang.Abstract):
    @abc.abstractmethod
    def invoke(self, request: ChatRequest) -> ta.Awaitable[ChatResponse]:
        raise NotImplementedError
