import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .generative import Generative
from .generative import GenerativeRequestOption
from .models import Model
from .models import Request
from .models import RequestOption
from .models import Response


##


@dc.dataclass(frozen=True)
class Prompt(lang.Final):
    s: str


##


PromptInput: ta.TypeAlias = Prompt
PromptNew: ta.TypeAlias = ta.Any
PromptOutput: ta.TypeAlias = str

PromptRequestOptions: ta.TypeAlias = RequestOption | GenerativeRequestOption


@dc.dataclass(frozen=True, kw_only=True)
class PromptRequest(
    Request[
        PromptInput,
        PromptRequestOptions,
        PromptNew,
    ],
    lang.Final,
):
    @dc.validate
    def _validate_v(self) -> bool:
        return isinstance(self.v, Prompt)


@dc.dataclass(frozen=True, kw_only=True)
class PromptResponse(Response[PromptOutput], lang.Final):
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
