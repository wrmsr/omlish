import abc
import typing as ta

from omlish import lang

from ...registries.globals import register_type
from ...services import Request
from ...services import Response
from ...services import Service
from ...types import Output
from ..messages import Chat
from .types import ChatChoices
from .types import ChatChoicesOptions


##


class ChatChoicesServiceOutput(Output, lang.Abstract, lang.Sealed):
    pass


ChatChoicesServiceOutputs: ta.TypeAlias = ChatChoicesServiceOutput


##


ChatChoicesRequest: ta.TypeAlias = Request[Chat, ChatChoicesOptions]

ChatChoicesResponse: ta.TypeAlias = Response[ChatChoices, ChatChoicesServiceOutputs]

# @om-manifest $.minichain.registries.manifests.RegistryTypeManifest
ChatChoicesService: ta.TypeAlias = Service[ChatChoicesRequest, ChatChoicesResponse]

register_type(ChatChoicesService, module=__name__)


def static_check_is_chat_choices_service[T: ChatChoicesService](t: type[T]) -> type[T]:
    return t


##


@static_check_is_chat_choices_service
class AbstractChatChoicesService(lang.Abstract):
    @abc.abstractmethod
    def invoke(self, request: ChatChoicesRequest) -> ta.Awaitable[ChatChoicesResponse]:
        raise NotImplementedError
