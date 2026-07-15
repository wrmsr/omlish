import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from ...core.streams import Stream
from .messages import AiMessage


##


@dc.dataclass(frozen=True)
class AiStreamEvent(lang.Abstract):
    pass


type AiStream = Stream[AiStreamEvent, AiMessage]


##


@ta.final
@dc.dataclass(frozen=True)
class StartAiStreamEvent(AiStreamEvent):
    pass


@ta.final
@dc.dataclass(frozen=True)
class EndAiStreamEvent(AiStreamEvent):
    pass


#


@ta.final
@dc.dataclass(frozen=True)
class TextStartAiStreamEvent(AiStreamEvent):
    pass


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class TextDeltaAiStreamEvent(AiStreamEvent):
    s: str


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class TextEndAiStreamEvent(AiStreamEvent):
    s: str
