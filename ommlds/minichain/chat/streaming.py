import typing as ta

from ..resources import ResourceManaged
from ..services import Response
from ..services import Service
from .choices import AiChoices
from .services import ChatRequest
from .services import ChatResponseOutputs


##


ChatStreamResponse: ta.TypeAlias = Response[ResourceManaged[ta.Iterator[AiChoices]], ChatResponseOutputs]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
ChatStreamService: ta.TypeAlias = Service[ChatRequest, ChatStreamResponse]
