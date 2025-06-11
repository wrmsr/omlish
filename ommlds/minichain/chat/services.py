import abc
import typing as ta

from omlish import lang

from ..llms.services import LlmRequestOption
from ..llms.services import LlmResponseOutput
from ..registry import register_type
from ..services import Request
from ..services import RequestOption
from ..services import Response
from ..services import ResponseOutput
from ..services import Service
from .messages import AiMessage
from .messages import Chat


##


class ChatRequestOption(RequestOption, lang.Abstract, lang.PackageSealed):
    pass


ChatRequestOptions = ChatRequestOption | LlmRequestOption


ChatRequest: ta.TypeAlias = Request[Chat, ChatRequestOptions]


##


class ChatResponseOutput(ResponseOutput, lang.Abstract, lang.PackageSealed):
    pass


ChatResponseOutputs = ChatResponseOutput | LlmResponseOutput


ChatResponse: ta.TypeAlias = Response[AiMessage, ChatResponseOutputs]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]

register_type(ChatService, module=__name__)


##


class AbstractChatService(ChatService, lang.Abstract):  # noqa
    @abc.abstractmethod
    def invoke(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError
