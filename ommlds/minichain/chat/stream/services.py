import abc
import typing as ta

from omlish import lang

from ...registry import register_type
from ...services import Request
from ...services import RequestOption
from ...services import ResponseOutput
from ...services import Service
from ...streaming import StreamResponse
from ..choices.services import ChatChoicesRequestOptions
from ..choices.services import ChatChoicesResponseOutputs
from ..choices.types import AiChoices
from ..messages import Chat


##


class ChatChoicesStreamRequestOption(RequestOption, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesStreamRequestOptions = ChatChoicesStreamRequestOption | ChatChoicesRequestOptions


ChatChoicesStreamRequest: ta.TypeAlias = Request[Chat, ChatChoicesStreamRequestOptions]


##


class ChatChoicesStreamResponseOutput(ResponseOutput, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesStreamResponseOutputs = ChatChoicesStreamResponseOutput


ChatChoicesStreamResponse: ta.TypeAlias = StreamResponse[
    AiChoices,
    ChatChoicesResponseOutputs,
    ChatChoicesStreamResponseOutput,
]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
ChatChoicesStreamService: ta.TypeAlias = Service[ChatChoicesStreamRequest, ChatChoicesStreamResponse]

register_type(ChatChoicesStreamService, module=__name__)


##


class AbstractChatChoicesStreamService(ChatChoicesStreamService, lang.Abstract):  # noqa
    @abc.abstractmethod
    def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        raise NotImplementedError
