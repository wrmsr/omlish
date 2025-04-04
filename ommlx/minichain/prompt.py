from omlish import dataclasses as dc
from omlish import lang

from .services import Request
from .services import RequestOption
from .services import Response
from .services import ResponseOutput
from .services import Service_


##


class PromptRequestOption(RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class PromptRequest(Request[PromptRequestOption]):
    prompt: str


##


class PromptResponseOutput(ResponseOutput, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class PromptResponse(Response[PromptResponseOutput]):
    text: str


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class PromptService(  # noqa
    Service_[
        PromptRequest,
        PromptResponse,
    ],
    lang.Abstract,
    request=PromptRequest,
    response=PromptResponse,
):
    pass
