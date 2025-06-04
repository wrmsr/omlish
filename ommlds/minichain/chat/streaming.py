import typing as ta

from ..services import Service
from .services import ChatResponseOutputs
from .choices import AiChoices
from .services import ChatRequest
from ..resources import ResourceManaged
from ..services import Response


##


ChatStreamResponse: ta.TypeAlias = Response[ResourceManaged[ta.Iterator[AiChoices]], ChatResponseOutputs]


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendTypeManifest
ChatStreamService: ta.TypeAlias = Service[ChatRequest, ChatStreamResponse]
