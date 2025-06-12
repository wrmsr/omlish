import abc
import typing as ta

from omlish import lang

from ...registry import register_type
from ...services import Request
from ...services import Service
from ...stream import StreamResponse
from ...types import Option
from ...types import Output
from ..choices.services import ChatChoicesOptions
from ..choices.services import ChatChoicesOutputs
from ..choices.types import AiChoices
from ..messages import Chat


##


class ChatChoicesStreamOption(Option, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesStreamOptions = ChatChoicesStreamOption | ChatChoicesOptions


ChatChoicesStreamRequest: ta.TypeAlias = Request[Chat, ChatChoicesStreamOptions]


##


class ChatChoicesStreamOutput(Output, lang.Abstract, lang.PackageSealed):
    pass


ChatChoicesStreamOutputs = ChatChoicesStreamOutput


ChatChoicesStreamResponse: ta.TypeAlias = StreamResponse[
    AiChoices,
    ChatChoicesOutputs,
    ChatChoicesStreamOutput,
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
