import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .generative import Generative
from .generative import GenerativeRequestOption
from .models import Model
from .models import ModelRequest
from .models import ModelRequestOption
from .models import ModelResponse


##


PromptInput: ta.TypeAlias = str
PromptNew: ta.TypeAlias = str
PromptOutput: ta.TypeAlias = str

PromptRequestOptions: ta.TypeAlias = ModelRequestOption | GenerativeRequestOption


@dc.dataclass(frozen=True, kw_only=True)
class PromptRequest(
    ModelRequest[
        PromptInput,
        PromptRequestOptions,
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


class PromptModel(
    Model[
        PromptRequest,
        PromptRequestOptions,
        PromptNew,
        PromptResponse,
    ],
    Generative,
    lang.Abstract,
):
    @abc.abstractmethod
    def invoke(self, request: PromptRequest) -> PromptResponse:
        raise NotImplementedError
