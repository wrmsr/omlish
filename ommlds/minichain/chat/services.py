import abc
import typing as ta

from omlish import lang

from ..registries.globals import register_type
from ..services import Request
from ..services import Response
from ..services import Service
from .messages import AiMessage
from .messages import Chat
from .types import ChatOptions
from .types import ChatOutputs


##


ChatRequest: ta.TypeAlias = Request[Chat, ChatOptions]

ChatResponse: ta.TypeAlias = Response[AiMessage, ChatOutputs]

# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]

register_type(ChatService, module=__name__)


def static_check_is_chat_service[T: ChatService](t: type[T]) -> type[T]:
    return t


##


@static_check_is_chat_service
class AbstractChatService(lang.Abstract):  # noqa
    @abc.abstractmethod
    def invoke(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError
