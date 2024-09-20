import dataclasses as dc
import typing as ta

from omlish import lang

from .models import Model


#


@dc.dataclass(frozen=True)
class Prompt(lang.Final):
    s: str


PromptModel: ta.TypeAlias = Model[Prompt, str]
