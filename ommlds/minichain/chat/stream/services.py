import abc
import typing as ta

from omlish import lang

from ...registry import register_type
from ...services import Request
from ...services import Service
from ...stream import StreamResponse
from ..choices.types import AiChoices
from ..choices.types import ChatChoicesOutputs
from ..messages import Chat
from .types import ChatChoicesStreamOptions
from .types import ChatChoicesStreamOutputs


##


ChatChoicesStreamRequest: ta.TypeAlias = Request[Chat, ChatChoicesStreamOptions]


ChatChoicesStreamResponse: ta.TypeAlias = StreamResponse[
    AiChoices,
    ChatChoicesOutputs,
    ChatChoicesStreamOutputs,
]

# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
ChatChoicesStreamService: ta.TypeAlias = Service[ChatChoicesStreamRequest, ChatChoicesStreamResponse]

register_type(ChatChoicesStreamService, module=__name__)


##


class AbstractChatChoicesStreamService(ChatChoicesStreamService, lang.Abstract):  # noqa
    @abc.abstractmethod
    def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        raise NotImplementedError
