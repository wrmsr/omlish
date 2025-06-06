import typing as ta

from omlish import lang

from ..registry import register_type
from ..services import ResponseOutput
from ..services import Service
from ..streaming import StreamResponse
from .choices import AiChoices
from .services import ChatRequest
from .services import ChatResponseOutputs


##


class ChatStreamResponseOutput(ResponseOutput, lang.Abstract, lang.PackageSealed):
    pass


ChatStreamResponse: ta.TypeAlias = StreamResponse[AiChoices, ChatResponseOutputs, ChatStreamResponseOutput]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
ChatStreamService: ta.TypeAlias = Service[ChatRequest, ChatStreamResponse]

register_type(ChatStreamService, module=__name__)
