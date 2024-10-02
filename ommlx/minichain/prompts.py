import abc

from omlish import dataclasses as dc
from omlish import lang

from .models import Model


##


@dc.dataclass(frozen=True)
class Prompt(lang.Final):
    s: str


class PromptModel(Model['PromptModel.Request', 'PromptModel.Response'], lang.Abstract):
    @dc.dataclass(frozen=True, kw_only=True)
    class Request(Model.Request[Prompt, Model.RequestOption]):
        pass

    @dc.dataclass(frozen=True, kw_only=True)
    class Response(Model.Response[str]):
        pass

    @abc.abstractmethod
    def generate(self, request: Request) -> Response:
        raise NotImplementedError
