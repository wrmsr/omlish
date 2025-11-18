import abc
import typing as ta

from omlish import lang

from ....registries.globals import register_type
from ....services import Request
from ....services import Service
from ....stream.services import StreamResponse
from ...messages import Chat
from ..types import ChatChoicesOutputs
from .types import AiChoicesDeltas
from .types import ChatChoicesStreamOptions
from .types import ChatChoicesStreamOutputs


##


ChatChoicesStreamRequest: ta.TypeAlias = Request[Chat, ChatChoicesStreamOptions]

ChatChoicesStreamResponse: ta.TypeAlias = StreamResponse[
    AiChoicesDeltas,
    ChatChoicesOutputs,
    ChatChoicesStreamOutputs,
]

# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
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
