import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .generative import Generative
from .generative import GenerativeOption
from .models import Model
from .models import ModelOption
from .models import ModelRequest
from .models import ModelResponse
from .services import ServiceOption


##


PromptInput: ta.TypeAlias = str
PromptNew: ta.TypeAlias = str
PromptOutput: ta.TypeAlias = str

PromptOptions: ta.TypeAlias = ServiceOption | ModelOption | GenerativeOption


@dc.dataclass(frozen=True, kw_only=True)
class PromptRequest(
    ModelRequest[
        PromptInput,
        PromptOptions,
        PromptNew,
    ],
    lang.Final,
):
    @dc.validate
    def _validate_v(self) -> bool:
        return isinstance(self.v, str)


@dc.dataclass(frozen=True, kw_only=True)
class PromptResponse(ModelResponse[PromptOutput], lang.Final):
    pass


# @omlish-manifest ommlx.minichain.backends.manifests.BackendTypeManifest
class PromptModel(  # noqa
    Model[
        PromptRequest,
        PromptOptions,
        PromptNew,
        PromptResponse,
    ],
    Generative,
    lang.Abstract,
):
    pass
