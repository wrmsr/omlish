import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .llms.services import LlmRequestOption
from .llms.services import LlmResponseOutput
from .services import Request
from .services import RequestOption
from .services import Response
from .services import ResponseOutput
from .services import Service_


CompletionRequestT = ta.TypeVar('CompletionRequestT', bound='CompletionRequest')
CompletionResponseT = ta.TypeVar('CompletionResponseT', bound='CompletionResponse')


##


class CompletionRequestOption(RequestOption, lang.Abstract):
    pass


# Cannot use forward refs due to _ServiceTypedValuesHolder reflection.
CompletionRequestOptionT = ta.TypeVar('CompletionRequestOptionT', bound=CompletionRequestOption | LlmRequestOption)


@dc.dataclass(frozen=True)
class CompletionRequest(Request[CompletionRequestOptionT]):
    prompt: str


##


class CompletionResponseOutput(ResponseOutput, lang.Abstract):
    pass


# Cannot use forward refs due to _ServiceTypedValuesHolder reflection.
CompletionResponseOutputT = ta.TypeVar('CompletionResponseOutputT', bound=CompletionResponseOutput | LlmResponseOutput)


@dc.dataclass(frozen=True)
class CompletionResponse(Response[CompletionResponseOutputT]):
    text: str


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendTypeManifest
class CompletionService(  # noqa
    Service_[
        CompletionRequestT,
        CompletionResponseT,
    ],
    lang.Abstract,
    ta.Generic[
        CompletionRequestT,
        CompletionResponseT,
    ],
    request=CompletionRequest,
    response=CompletionResponse,
):
    pass
