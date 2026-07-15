import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from ...core.streams import Stream
from .messages import AiMessage
from .messages import ToolCall


##


@dc.dataclass(frozen=True)
class AiStreamEvent(lang.Abstract):
    pass


type AiStream = Stream[AiStreamEvent, AiMessage]


##


@ta.final
@dc.dataclass(frozen=True)
class StreamStartAiStreamEvent(AiStreamEvent):
    pass


@ta.final
@dc.dataclass(frozen=True)
class StreamEndAiStreamEvent(AiStreamEvent):
    pass


#


@dc.dataclass(frozen=True)
class ContentAiStreamEvent(AiStreamEvent, lang.Abstract):
    content_index: int = dc.field(kw_only=True)


#


@ta.final
@dc.dataclass(frozen=True)
class TextStartAiStreamEvent(ContentAiStreamEvent):
    pass


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class TextDeltaAiStreamEvent(ContentAiStreamEvent):
    text: str


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class TextEndAiStreamEvent(ContentAiStreamEvent):
    text: str


#


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class ToolCallStartAiStreamEvent(ContentAiStreamEvent):
    pass


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class ToolCallDeltaAiStreamEvent(ContentAiStreamEvent):
    text: str


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True, terse_repr=True)
class ToolCallEndAiStreamEvent(ContentAiStreamEvent):
    tool_call: ToolCall
