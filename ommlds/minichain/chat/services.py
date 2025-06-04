import typing as ta

from ..llms.services import LlmRequestOption
from ..llms.services import LlmResponseOutput
from ..services import Request
from ..services import Response
from ..services import Service
from .choices import AiChoices
from .messages import Chat
from .types import ChatRequestOption
from .types import ChatResponseOutput


##


ChatRequestOptions = ChatRequestOption | LlmRequestOption


ChatRequest: ta.TypeAlias = Request[Chat, ChatRequestOptions]


##


ChatResponseOutputs = ChatResponseOutput | LlmResponseOutput


ChatResponse: ta.TypeAlias = Response[AiChoices, ChatResponseOutputs]


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendTypeManifest
ChatService: ta.TypeAlias = Service[ChatRequest, ChatResponse]
