import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from ...core.streams import Stream
from .messages import AiMessage


##


@dc.dataclass(frozen=True)
class AiEvent(lang.Abstract):
    pass


type AiStream = Stream[AiEvent, AiMessage]


##


@ta.final
@dc.dataclass(frozen=True)
class StartAiEvent(AiEvent):
    pass


@ta.final
@dc.dataclass(frozen=True)
class EndAiEvent(AiEvent):
    pass
