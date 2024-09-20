import abc
import dataclasses as dc
import typing as ta

from omlish import lang

from .models import Model
from .models import Request
from .models import Response


#


@dc.dataclass(frozen=True)
class Prompt(lang.Final):
    s: str


PromptModel: ta.TypeAlias = Model[Prompt, str]


class PromptModel_(PromptModel, lang.Abstract):  # noqa
    @abc.abstractmethod
    def generate(self, request: Request[Prompt]) -> Response[str]:
        raise NotImplementedError
