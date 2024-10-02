import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .models import Model
from .models import Request
from .models import RequestOption
from .models import Response


##


PromptRequestOptions: ta.TypeAlias = RequestOption


@dc.dataclass(frozen=True)
class Prompt(lang.Final):
    s: str


@dc.dataclass(frozen=True, kw_only=True)
class PromptRequest(Request[Prompt, PromptRequestOptions], lang.Final):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class PromptResponse(Response[str], lang.Final):
    pass


class PromptModel(Model[PromptRequest, PromptRequestOptions, PromptResponse], lang.Abstract):
    @abc.abstractmethod
    def generate(self, request: PromptRequest) -> PromptResponse:
        raise NotImplementedError
