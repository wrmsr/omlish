import abc
import typing as ta

from omlish import lang

from ...registry import register_type
from ...services import Request
from ...services import Response
from ...services import Service
from ...types import Option
from ...types import Output
from ..messages import Chat
from ..services import ChatOptions
from ..services import ChatOutputs
from .types import AiChoices


##


class ChatChoicesOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesOptions = ChatChoicesOption | ChatOptions


ChatChoicesRequest: ta.TypeAlias = Request[Chat, ChatChoicesOptions]


##


class ChatChoicesOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesOutputs = ChatChoicesOutput | ChatOutputs


ChatChoicesResponse: ta.TypeAlias = Response[AiChoices, ChatChoicesOutputs]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
ChatChoicesService: ta.TypeAlias = Service[ChatChoicesRequest, ChatChoicesResponse]

register_type(ChatChoicesService, module=__name__)


##


class AbstractChatChoicesService(ChatChoicesService, lang.Abstract):  # noqa
    @abc.abstractmethod
    def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        raise NotImplementedError
