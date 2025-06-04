import typing as ta

from omlish import lang

from .llms.services import LlmRequestOption
from .llms.services import LlmResponseOutput
from .registry import register_type
from .services import Request
from .services import RequestOption
from .services import Response
from .services import ResponseOutput
from .services import Service


##


class CompletionRequestOption(RequestOption, lang.Abstract, lang.Sealed):
    pass


CompletionRequestOptions: ta.TypeAlias = CompletionRequestOption | LlmRequestOption


CompletionRequest: ta.TypeAlias = Request[str, CompletionRequestOptions]


##


class CompletionResponseOutput(ResponseOutput, lang.Abstract, lang.Sealed):
    pass


CompletionResponseOutputs: ta.TypeAlias = CompletionResponseOutput | LlmResponseOutput


CompletionResponse: ta.TypeAlias = Response[str, CompletionResponseOutputs]


##


# @omlish-manifest ommlds.minichain.registry.RegistryTypeManifest
CompletionService: ta.TypeAlias = Service[CompletionRequest, CompletionResponse]

register_type(CompletionService, module=__name__)
