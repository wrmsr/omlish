import abc
import typing as ta

from omcore import lang

from ....registries.globals import register_type
from ....services import Request
from ....services import Service
from ....services import StreamResponse
from ....types import Output
from ...messages import Chat
from .types import AiChoicesDeltas
from .types import ChatChoicesStreamOptions
from .types import ChatChoicesStreamResult


##


class ChatChoicesStreamServiceOutput(Output, lang.Abstract, lang.Sealed):
    pass


ChatChoicesStreamServiceOutputs: ta.TypeAlias = ChatChoicesStreamServiceOutput


##


ChatChoicesStreamRequest: ta.TypeAlias = Request[Chat, ChatChoicesStreamOptions]

ChatChoicesStreamResponse: ta.TypeAlias = StreamResponse[
    AiChoicesDeltas,
    ChatChoicesStreamResult,
    ChatChoicesStreamServiceOutputs,
]

# @om-manifest $.minichain.registries.manifests.RegistryTypeManifest
ChatChoicesStreamService: ta.TypeAlias = Service[ChatChoicesStreamRequest, ChatChoicesStreamResponse]

register_type(ChatChoicesStreamService, module=__name__)


def static_check_is_chat_choices_stream_service[T: ChatChoicesStreamService](t: type[T]) -> type[T]:
    return t


##


@static_check_is_chat_choices_stream_service
class AbstractChatChoicesStreamService(lang.Abstract):
    @abc.abstractmethod
    def invoke(self, request: ChatChoicesStreamRequest) -> ta.Awaitable[ChatChoicesStreamResponse]:
        raise NotImplementedError
