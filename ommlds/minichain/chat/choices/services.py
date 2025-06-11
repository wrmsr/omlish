import abc
import typing as ta

from omlish import lang

from ...registry import register_type
from ...services import Request
from ...services import RequestOption
from ...services import Response
from ...services import ResponseOutput
from ...services import Service
from ..messages import Chat
from ..simple.services import ChatRequestOptions
from ..simple.services import ChatResponseOutputs
from .types import AiChoices


##


class ChatChoicesRequestOption(RequestOption, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesRequestOptions = ChatChoicesRequestOption | ChatRequestOptions


ChatChoicesRequest: ta.TypeAlias = Request[Chat, ChatChoicesRequestOptions]


##


class ChatChoicesResponseOutput(ResponseOutput, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesResponseOutputs = ChatChoicesResponseOutput | ChatResponseOutputs


ChatChoicesResponse: ta.TypeAlias = Response[AiChoices, ChatChoicesResponseOutputs]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
ChatChoicesService: ta.TypeAlias = Service[ChatChoicesRequest, ChatChoicesResponse]

register_type(ChatChoicesService, module=__name__)


##


class AbstractChatChoicesService(ChatChoicesService, lang.Abstract):  # noqa
    @abc.abstractmethod
    def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        raise NotImplementedError
