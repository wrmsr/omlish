import abc
import typing as ta

from omlish import lang

from ..llms.services import LlmOption
from ..llms.services import LlmOutput
from ..registry import register_type
from ..services import Request
from ..services import Response
from ..services import Service
from ..types import Option
from ..types import Output
from .messages import AiMessage
from .messages import Chat


##


class ChatOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatOptions = ChatOption | LlmOption


ChatRequest: ta.TypeAlias = Request[Chat, ChatOptions]


##


class ChatOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatOutputs = ChatOutput | LlmOutput


ChatResponse: ta.TypeAlias = Response[AiMessage, ChatOutputs]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]

register_type(ChatService, module=__name__)


##


class AbstractChatService(ChatService, lang.Abstract):  # noqa
    @abc.abstractmethod
    def invoke(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError
