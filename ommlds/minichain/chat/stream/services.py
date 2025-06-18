import abc
import typing as ta

from omlish import lang

from ...registry import register_type
from ...services import Request
from ...services import Service
from ...stream.services import StreamResponse
from ..choices.types import ChatChoicesOutputs
from ..messages import Chat
from .types import AiChoiceDeltas
from .types import ChatChoicesStreamOptions
from .types import ChatChoicesStreamOutputs


##


ChatChoicesStreamRequest: ta.TypeAlias = Request[Chat, ChatChoicesStreamOptions]

ChatChoicesStreamResponse: ta.TypeAlias = StreamResponse[
    AiChoiceDeltas,
    ChatChoicesOutputs,
    ChatChoicesStreamOutputs,
]

# @omlish-manifest $.minichain.registry.RegistryTypeManifest
ChatChoicesStreamService: ta.TypeAlias = Service[ChatChoicesStreamRequest, ChatChoicesStreamResponse]

register_type(ChatChoicesStreamService, module=__name__)


def static_check_is_chat_choices_stream_service[T: ChatChoicesStreamService](t: type[T]) -> type[T]:
    return t


##


@static_check_is_chat_choices_stream_service
class AbstractChatChoicesStreamService(lang.Abstract):  # noqa
    @abc.abstractmethod
    def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        raise NotImplementedError


##


ChatChoicesStreamGenerator: ta.TypeAlias = ta.Generator[AiChoiceDeltas, None, ta.Sequence[ChatChoicesOutputs] | None]
