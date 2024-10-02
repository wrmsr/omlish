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
PromptOutput: ta.TypeAlias = str

PromptRequestOptions: ta.TypeAlias = RequestOption | GenerativeRequestOption


@dc.dataclass(frozen=True, kw_only=True)
class PromptRequest(Request[PromptInput, PromptRequestOptions], lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class PromptResponse(Response[PromptOutput], lang.Final):
    pass


class PromptModel(Model[PromptRequest, PromptRequestOptions, PromptResponse], Generative, lang.Abstract):
    @abc.abstractmethod
    def invoke(self, request: PromptRequest) -> PromptResponse:
        raise NotImplementedError
