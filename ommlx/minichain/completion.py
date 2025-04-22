from omlish import dataclasses as dc
from omlish import lang

from .services import Request
from .services import RequestOption
from .services import Response
from .services import ResponseOutput
from .services import Service_


##


class CompletionRequestOption(RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class CompletionRequest(Request[CompletionRequestOption]):
    prompt: str


##


class CompletionResponseOutput(ResponseOutput, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class CompletionResponse(Response[CompletionResponseOutput]):
    text: str


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class CompletionService(  # noqa
    Service_[
        CompletionRequest,
        CompletionResponse,
    ],
    lang.Abstract,
    request=CompletionRequest,
    response=CompletionResponse,
):
    pass
