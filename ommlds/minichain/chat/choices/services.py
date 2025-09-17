import abc
import typing as ta

from omlish import lang

from ...registries.globals import register_type
from ...services import Request
from ...services import Response
from ...services import Service
from ..messages import Chat
from .types import AiChoices
from .types import ChatChoicesOptions
from .types import ChatChoicesOutputs


##


ChatChoicesRequest: ta.TypeAlias = Request[Chat, ChatChoicesOptions]

ChatChoicesResponse: ta.TypeAlias = Response[AiChoices, ChatChoicesOutputs]

# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
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
