import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .messages import AiMessage


##


@dc.dataclass(frozen=True)
class AiChoice(lang.Final):
    m: AiMessage


AiChoices: ta.TypeAlias = ta.Sequence[AiChoice]
